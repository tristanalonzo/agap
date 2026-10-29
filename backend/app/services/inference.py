"""Cyclone category inference.

Which path runs is decided by settings.MOCK_INFERENCE:

    True  (the default) -> a fake "demo" result, always flagged as fake.
    False               -> the real ONNX model at settings.ONNX_MODEL_PATH.

Flipping the flag can never produce a made-up category: with MOCK_INFERENCE false and
anything missing, get_cyclone_assessment() returns an honest "unavailable" that names
what is missing (AGENTS.md safety rules 1 and 2).

Two things are still missing, and only Team A can give them to us. This file does not
guess at either of them (AGENTS.md section 10):

    1. static/preprocessing.json -- the input name, shape, dtype, normalization and
       class order of their model. load_preprocessing() reads it; it invents no values,
       so a missing or incomplete file raises ModelNotReady with the key that is absent.
    2. A satellite frame to classify. /assess receives a latitude and longitude only,
       so there is no image to feed the model. Picking the frame source is still an open
       question in docs/PROGRESS.md.

Because of (2), classify() takes a frame that is already preprocessed and is called by
the tests today, and by whatever supplies frames in Phase 3. Nothing in this file
preprocesses an image, since that is exactly the part we must not invent.
"""

import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import MANILA_TZ, settings
from app.schemas import CycloneAssessment

PREPROCESSING_FILE = Path(__file__).parent.parent / "static" / "preprocessing.json"

# backend/. A relative ONNX_MODEL_PATH is read from here, not from wherever the server was
# started, so the model is found whichever folder you run uvicorn or pytest from.
BACKEND_DIR = Path(__file__).parent.parent.parent

# The five PAGASA categories, for display only. The order the model actually uses comes
# from class_order in preprocessing.json, never from this dict.
CATEGORY_NAMES = {
    "TD": "Tropical Depression",
    "TS": "Tropical Storm",
    "STS": "Severe Tropical Storm",
    "TY": "Typhoon",
    "STY": "Super Typhoon",
}

# Keys preprocessing.json must contain. Listed in the Phase 3 handoff checklist.
REQUIRED_KEYS = ("input_name", "input_shape", "dtype", "class_order", "normalization")

# Loaded once each, the first time they are needed.
_config: "ModelConfig | None" = None
_session: Any | None = None


class ModelNotReady(RuntimeError):
    """The real model cannot run yet, and the message says what is missing."""


@dataclass(frozen=True)
class ModelConfig:
    """What Team A tells us about their model. Every field comes from preprocessing.json."""

    input_name: str
    input_shape: list[int]
    dtype: str
    class_order: list[str]
    normalization: dict[str, Any]
    model_version: str


def load_preprocessing(path: Path | None = None) -> ModelConfig:
    """Read preprocessing.json. Raises ModelNotReady if it is absent or incomplete."""
    # Looked up when called, not as a default argument: a default is fixed once at import,
    # which would make changing PREPROCESSING_FILE (as the tests do) silently do nothing.
    if path is None:
        path = PREPROCESSING_FILE
    if not path.exists():
        raise ModelNotReady(
            f"preprocessing.json not found at {path}. Team A still owes us the input name, "
            "shape, dtype, normalization steps and class order (see docs/PROGRESS.md)."
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ModelNotReady(f"preprocessing.json at {path} is not valid JSON: {error}") from error

    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise ModelNotReady(
            f"preprocessing.json at {path} is missing {', '.join(missing)}. "
            "Ask Team A for those before turning MOCK_INFERENCE off."
        )

    # A repeated name (a typo like TS, TS) would let two different scores mean the same
    # category, which is the same wrong-category risk as a count mismatch.
    class_order = data["class_order"]
    if not class_order or len(set(class_order)) != len(class_order):
        raise ModelNotReady(
            f"preprocessing.json's class_order must name each class exactly once: {class_order}."
        )

    unknown = [name for name in class_order if name not in CATEGORY_NAMES]
    if unknown:
        raise ModelNotReady(
            f"preprocessing.json lists class(es) we do not know: {', '.join(unknown)}. "
            f"Expected only {', '.join(CATEGORY_NAMES)}."
        )

    return ModelConfig(
        input_name=data["input_name"],
        input_shape=data["input_shape"],
        dtype=data["dtype"],
        class_order=data["class_order"],
        normalization=data["normalization"],
        # Optional: if Team A does not name a version we record the file we loaded.
        model_version=data.get("model_version", Path(settings.ONNX_MODEL_PATH).name),
    )


def get_config() -> ModelConfig:
    global _config
    if _config is None:
        _config = load_preprocessing()
    return _config


def model_path() -> Path:
    """Where the .onnx file should be. A relative setting is read from backend/."""
    path = Path(settings.ONNX_MODEL_PATH)
    return path if path.is_absolute() else BACKEND_DIR / path


def load_session(path: Path | None = None) -> Any:
    """Open the ONNX model. Raises ModelNotReady if the file or onnxruntime is missing."""
    weights = model_path() if path is None else path
    if not weights.exists():
        raise ModelNotReady(
            f"Model file not found at {weights}. Put agap_tc_classifier.onnx there "
            "(or download it from the team Drive -- see README)."
        )
    try:
        # Imported here, not at the top, so the app still starts without onnxruntime
        # installed. requirements.txt says which lines to uncomment for Phase 3.
        import onnxruntime
    except ImportError as error:
        raise ModelNotReady(
            "onnxruntime is not installed. Uncomment the Phase 3 lines in "
            "backend/requirements.txt and run pip install -r requirements.txt."
        ) from error
    try:
        return onnxruntime.InferenceSession(str(weights), providers=["CPUExecutionProvider"])
    except Exception as error:
        # Any failure to open the file -- corrupt, an opset this onnxruntime is too old for,
        # or the HTML page Google Drive saves in place of a large file -- must become
        # "unavailable" on the cyclone card. onnxruntime raises its own exception types, so
        # without this one bad file would crash every /assess and take the rainfall warning
        # and nearest shelter down with it.
        raise ModelNotReady(f"Could not open the model at {weights}: {error}") from error


def get_session() -> Any:
    global _session
    if _session is None:
        _session = load_session()
    return _session


def clear_cache() -> None:
    """Forget the loaded config and model. Used by tests."""
    global _config, _session
    _config = None
    _session = None


def read_scores(output: Any) -> list[float]:
    """The class scores in the model's first output, for the one frame we sent.

    Accepts shape (1, n) -- one row per frame, the usual layout -- or (n,). Anything else is
    a layout Team A has not told us about, so we stop rather than guess which numbers are
    the scores.
    """
    shape = tuple(getattr(output, "shape", ()))
    if len(shape) == 2 and shape[0] == 1:
        return [float(score) for score in output[0]]
    if len(shape) == 1:
        return [float(score) for score in output]
    raise ModelNotReady(
        f"The model's first output has shape {shape or 'unknown'}, which we do not know how "
        "to read. Ask Team A which output holds the class scores, and its shape."
    )


def classify(frame: Any, observed_at: str | None = None) -> CycloneAssessment:
    """Run the model on one already-preprocessed frame.

    `frame` must already match config.input_shape and config.dtype: this function does no
    normalization of its own, because the steps are Team A's to specify, not ours to guess.
    """
    config = get_config()
    session = get_session()
    try:
        outputs = session.run(None, {config.input_name: frame})
    except Exception as error:
        # Most often the input name, shape or dtype in preprocessing.json does not match the
        # model. Say that, instead of passing onnxruntime's own exception upward.
        raise ModelNotReady(
            f"The model rejected the frame: {error}. Check input_name, input_shape and dtype "
            "in preprocessing.json against the model."
        ) from error
    scores = read_scores(outputs[0])

    # Exactly one score per class, or which score means which category is a guess. Checking
    # only the winning index would let a 3-class model pass against a 5-class list and be
    # read as the wrong category.
    if len(scores) != len(config.class_order):
        raise ModelNotReady(
            f"The model returned {len(scores)} scores but preprocessing.json lists "
            f"{len(config.class_order)} classes ({', '.join(config.class_order)}). "
            "Ask Team A which is right."
        )

    # NaN never wins or loses a comparison, so max() would pick an arbitrary category, and
    # the response could not even be sent as JSON. It usually means wrong preprocessing.
    if not all(math.isfinite(score) for score in scores):
        raise ModelNotReady(
            "The model returned a score that is not a number (NaN or infinity), which usually "
            "means the frame was preprocessed wrongly. Check the normalization steps."
        )

    best = max(range(len(scores)), key=lambda i: scores[i])
    code = config.class_order[best]

    return CycloneAssessment(
        status="live",
        is_demo=False,
        category_code=code,
        category_name=CATEGORY_NAMES[code],
        # Only Team A can say whether their model also predicts wind, and in what unit.
        sustained_wind_kph=None,
        confidence=float(scores[best]),
        # The raw score is not a calibrated probability, so we never present it as one.
        confidence_is_calibrated=False,
        model_version=config.model_version,
        observed_at=observed_at,
        inferred_at=datetime.now(MANILA_TZ).isoformat(timespec="seconds"),
        warnings=[
            "Model estimate, not an official PAGASA wind signal.",
            "Confidence is a raw model score, not a calibrated probability.",
        ],
    )


def mock_assessment() -> CycloneAssessment:
    """A fake Typhoon result, clearly marked as demo data (AGENTS.md safety rule 1)."""
    return CycloneAssessment(
        status="demo",
        is_demo=True,
        category_code="TY",
        category_name="Typhoon",
        sustained_wind_kph=140.0,
        confidence=None,
        confidence_is_calibrated=False,
        model_version=None,
        observed_at=None,
        inferred_at=datetime.now(MANILA_TZ).isoformat(timespec="seconds"),
        warnings=["Mock result for development. Not a real prediction."],
    )


def unavailable_assessment(reason: str) -> CycloneAssessment:
    """No category at all, and the reason why. Never a guess (AGENTS.md safety rule 2)."""
    return CycloneAssessment(
        status="unavailable",
        is_demo=False,
        category_code="unknown",
        category_name="Unknown",
        sustained_wind_kph=None,
        confidence=None,
        confidence_is_calibrated=False,
        model_version=None,
        observed_at=None,
        inferred_at=datetime.now(MANILA_TZ).isoformat(timespec="seconds"),
        warnings=[reason],
    )


def get_cyclone_assessment() -> CycloneAssessment:
    """The cyclone card's data for /assess: mock, or an honest "unavailable"."""
    if settings.MOCK_INFERENCE:
        return mock_assessment()

    # MOCK_INFERENCE is off, so the caller wants a real prediction. Say precisely why
    # there is none instead of quietly falling back to the mock.
    try:
        get_config()
        get_session()
    except ModelNotReady as error:
        return unavailable_assessment(f"No cyclone estimate: {error}")

    return unavailable_assessment(
        "No cyclone estimate: the model is loaded but /assess has no satellite frame to "
        "classify. Choosing the frame source is an open question (see docs/PROGRESS.md)."
    )
