"""Tests for the mock path, the preprocessing.json reader, and the honest "unavailable".

The real-model test is skipped until Team A delivers agap_tc_classifier.onnx and a real
preprocessing.json. Nothing here needs onnxruntime installed.
"""

import json
from pathlib import Path

import pytest

from app.config import settings
from app.services import inference

FIXTURES = Path(__file__).parent / "fixtures"
EXAMPLE_PREPROCESSING = FIXTURES / "preprocessing_example.json"


@pytest.fixture(autouse=True)
def fresh_inference_cache() -> None:
    inference.clear_cache()


def test_mock_result_is_always_flagged_as_demo() -> None:
    result = inference.mock_assessment()
    assert result.status == "demo"
    assert result.is_demo is True
    # Safety rule 1: a mock result always carries a warning.
    assert result.warnings


def test_assess_uses_the_mock_while_mock_inference_is_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "MOCK_INFERENCE", True)
    assert inference.get_cyclone_assessment().is_demo is True


def test_mock_off_without_the_model_says_unavailable_not_a_guess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "MOCK_INFERENCE", False)
    monkeypatch.setattr(inference, "PREPROCESSING_FILE", FIXTURES / "does_not_exist.json")

    result = inference.get_cyclone_assessment()
    assert result.status == "unavailable"
    # Never a fake category, and never silently the mock either.
    assert result.is_demo is False
    assert result.category_code == "unknown"
    assert result.confidence is None
    # The warning has to say what is missing.
    assert "preprocessing.json" in result.warnings[0]


def test_load_preprocessing_reads_every_field() -> None:
    config = inference.load_preprocessing(EXAMPLE_PREPROCESSING)
    assert config.input_name == "input"
    assert config.dtype == "float32"
    assert config.class_order == ["TD", "TS", "STS", "TY", "STY"]
    assert config.model_version == "example-0.0.0"


def test_missing_file_names_the_path() -> None:
    with pytest.raises(inference.ModelNotReady, match="not found"):
        inference.load_preprocessing(FIXTURES / "does_not_exist.json")


def test_missing_key_is_named(tmp_path: Path) -> None:
    incomplete = json.loads(EXAMPLE_PREPROCESSING.read_text(encoding="utf-8"))
    del incomplete["class_order"]
    path = tmp_path / "preprocessing.json"
    path.write_text(json.dumps(incomplete), encoding="utf-8")

    with pytest.raises(inference.ModelNotReady, match="class_order"):
        inference.load_preprocessing(path)


def test_unknown_class_name_is_rejected(tmp_path: Path) -> None:
    wrong = json.loads(EXAMPLE_PREPROCESSING.read_text(encoding="utf-8"))
    wrong["class_order"] = ["TD", "TS", "HURRICANE"]
    path = tmp_path / "preprocessing.json"
    path.write_text(json.dumps(wrong), encoding="utf-8")

    with pytest.raises(inference.ModelNotReady, match="HURRICANE"):
        inference.load_preprocessing(path)


def test_missing_weights_tell_you_where_to_put_them(tmp_path: Path) -> None:
    with pytest.raises(inference.ModelNotReady, match="Model file not found"):
        inference.load_session(tmp_path / "agap_tc_classifier.onnx")


@pytest.mark.skipif(
    not Path(settings.ONNX_MODEL_PATH).exists(),
    reason="Team A has not delivered agap_tc_classifier.onnx yet (Phase 3)",
)
def test_real_model_returns_one_of_the_five_categories() -> None:
    """Unskips itself the moment the real model and preprocessing.json are in place.

    Team A also owes us 3-5 preprocessed .npy frames with their expected classes. Once
    those arrive, replace this smoke test with one case per frame (Phase 3 handoff list).
    """
    import numpy

    config = inference.get_config()
    frame = numpy.zeros(config.input_shape, dtype=config.dtype)

    result = inference.classify(frame)
    assert result.category_code in inference.CATEGORY_NAMES
    assert result.is_demo is False
    assert result.confidence_is_calibrated is False
