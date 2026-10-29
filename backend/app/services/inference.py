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
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import MANILA_TZ, settings
from app.schemas import CycloneAssessment

PREPROCESSING_FILE = Path(__file__).parent.parent / "static" / "preprocessing.json"

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


def load_preprocessing(path: Path = PREPROCESSING_FILE) -> ModelConfig:
    """Read preprocessing.json. Raises ModelNotReady if it is absent or incomplete."""
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

    unknown = [name for name in data["class_order"] if name not in CATEGORY_NAMES]
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


def load_session(path: Path | None = None) -> Any:
    """Open the ONNX model. Raises ModelNotReady if the file or onnxruntime is missing."""
    weights = Path(settings.ONNX_MODEL_PATH) if path is None else path
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
    return onnxruntime.InferenceSession(str(weights), providers=["CPUExecutionProvider"])


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


def classify(frame: Any, observed_at: str | None = None) -> CycloneAssessment:
    """Run the model on one already-preprocessed frame.

    `frame` must already match config.input_shape and config.dtype: this function does no
    normalization of its own, because the steps are Team A's to specify, not ours to guess.
    """
    config = get_config()
    outputs = get_session().run(None, {config.input_name: frame})
    scores = list(outputs[0][0])

    best = max(range(len(scores)), key=lambda i: scores[i])
    if best >= len(config.class_order):
        raise ModelNotReady(
            f"The model returned {len(scores)} scores but preprocessing.json lists "
            f"{len(config.class_order)} classes. Ask Team A which is right."
        )
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
