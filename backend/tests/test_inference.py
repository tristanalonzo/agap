"""Tests for the mock path, the preprocessing.json reader, and the honest "unavailable".

The real-model test is skipped until Team A delivers agap_tc_classifier.onnx and a real
preprocessing.json. Nothing here needs onnxruntime installed.
"""

import json
import sys
import types
from collections.abc import Iterator
from pathlib import Path

import pytest

from app.config import settings
from app.services import inference

FIXTURES = Path(__file__).parent / "fixtures"
EXAMPLE_PREPROCESSING = FIXTURES / "preprocessing_example.json"


@pytest.fixture(autouse=True)
def fresh_inference_cache() -> Iterator[None]:
    # Cleared after as well as before, so a config loaded here never leaks into another file.
    inference.clear_cache()
    yield
    inference.clear_cache()


def fake_onnxruntime_that_cannot_open(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stand in for onnxruntime failing to open a file, with an exception type of its own."""

    class InvalidProtobuf(Exception):
        pass

    def inference_session(path: str, providers: list[str]) -> None:
        raise InvalidProtobuf(f"Load model from {path} failed: Protobuf parsing failed.")

    monkeypatch.setitem(
        sys.modules, "onnxruntime", types.SimpleNamespace(InferenceSession=inference_session)
    )


def test_a_model_file_that_cannot_be_opened_is_unavailable_not_a_crash(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # For example the HTML page Google Drive saves in place of a large file.
    bad_model = tmp_path / "agap_tc_classifier.onnx"
    bad_model.write_text("<html>Google Drive can't scan this file for viruses</html>")
    fake_onnxruntime_that_cannot_open(monkeypatch)
    monkeypatch.setattr(settings, "MOCK_INFERENCE", False)
    monkeypatch.setattr(settings, "ONNX_MODEL_PATH", str(bad_model))
    monkeypatch.setattr(inference, "PREPROCESSING_FILE", EXAMPLE_PREPROCESSING)

    result = inference.get_cyclone_assessment()
    assert result.status == "unavailable"
    assert "Could not open the model" in result.warnings[0]


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


def test_changing_preprocessing_file_really_changes_what_is_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Guards the test above: with a valid config in place the complaint must move on to the
    # model file. If PREPROCESSING_FILE were fixed at import, both tests would read the same
    # file and this one would fail.
    monkeypatch.setattr(settings, "MOCK_INFERENCE", False)
    monkeypatch.setattr(inference, "PREPROCESSING_FILE", EXAMPLE_PREPROCESSING)
    monkeypatch.setattr(settings, "ONNX_MODEL_PATH", "does/not/exist.onnx")

    result = inference.get_cyclone_assessment()
    assert result.status == "unavailable"
    assert "Model file not found" in result.warnings[0]


def test_relative_model_path_is_read_from_the_backend_folder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "ONNX_MODEL_PATH", "app/weights/agap_tc_classifier.onnx")
    expected = Path(inference.__file__).parents[2] / "app" / "weights" / "agap_tc_classifier.onnx"
    assert inference.model_path() == expected


class FakeOutput(list):
    """Stands in for an onnxruntime output: a list that also has a shape."""

    def __init__(self, rows: list, shape: tuple) -> None:
        super().__init__(rows)
        self.shape = shape


class FakeSession:
    def __init__(self, output: FakeOutput) -> None:
        self.output = output

    def run(self, _names: None, _inputs: dict) -> list:
        return [self.output]


def use_fake_model(monkeypatch: pytest.MonkeyPatch, output: FakeOutput) -> None:
    monkeypatch.setattr(inference, "PREPROCESSING_FILE", EXAMPLE_PREPROCESSING)
    monkeypatch.setattr(inference, "get_session", lambda: FakeSession(output))


def test_classify_picks_the_highest_score_in_class_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Example class order is TD, TS, STS, TY, STY, so index 3 is TY.
    use_fake_model(monkeypatch, FakeOutput([[0.1, 0.2, 0.1, 0.5, 0.1]], (1, 5)))

    result = inference.classify(frame=None)
    assert result.category_code == "TY"
    assert result.status == "live"
    assert result.is_demo is False
    assert result.confidence == 0.5
    assert result.confidence_is_calibrated is False


def test_classify_reads_a_flat_output_too(monkeypatch: pytest.MonkeyPatch) -> None:
    use_fake_model(monkeypatch, FakeOutput([0.9, 0.0, 0.0, 0.0, 0.1], (5,)))
    assert inference.classify(frame=None).category_code == "TD"


def test_classify_refuses_fewer_scores_than_classes(monkeypatch: pytest.MonkeyPatch) -> None:
    # A 3-class model against a 5-class list. The winning index (1) is inside the list, so
    # checking only the index would wrongly report "TS". The counts must match.
    use_fake_model(monkeypatch, FakeOutput([[0.1, 0.8, 0.1]], (1, 3)))

    with pytest.raises(inference.ModelNotReady, match="3 scores but preprocessing.json lists 5"):
        inference.classify(frame=None)


def test_classify_refuses_an_output_layout_it_was_not_told_about(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Two rows for one frame: which row is ours is a guess, so stop.
    use_fake_model(monkeypatch, FakeOutput([[0.2] * 5, [0.2] * 5], (2, 5)))

    with pytest.raises(inference.ModelNotReady, match="shape"):
        inference.classify(frame=None)


class RejectingSession:
    def run(self, _names: None, _inputs: dict) -> list:
        # What onnxruntime says when preprocessing.json names an input the model lacks.
        raise RuntimeError("Invalid input name: input")


def test_classify_explains_a_frame_the_model_rejects(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(inference, "PREPROCESSING_FILE", EXAMPLE_PREPROCESSING)
    monkeypatch.setattr(inference, "get_session", lambda: RejectingSession())

    with pytest.raises(inference.ModelNotReady, match="Check input_name"):
        inference.classify(frame=None)


def test_classify_refuses_scores_that_are_not_numbers(monkeypatch: pytest.MonkeyPatch) -> None:
    # 0.5 should win, but NaN never loses a comparison, so without the check max() keeps
    # index 0 and reports TD.
    use_fake_model(monkeypatch, FakeOutput([[float("nan"), 0.2, 0.1, 0.5, 0.1]], (1, 5)))

    with pytest.raises(inference.ModelNotReady, match="not a number"):
        inference.classify(frame=None)


def test_a_broken_model_file_does_not_take_assess_down(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # The harm the "cannot be opened" test guards against: the whole response failing, and
    # the rainfall warning and nearest shelter going with it.
    from fastapi.testclient import TestClient

    from app.main import app

    bad_model = tmp_path / "agap_tc_classifier.onnx"
    bad_model.write_text("not a model")
    fake_onnxruntime_that_cannot_open(monkeypatch)
    monkeypatch.setattr(settings, "MOCK_INFERENCE", False)
    monkeypatch.setattr(settings, "ONNX_MODEL_PATH", str(bad_model))
    monkeypatch.setattr(inference, "PREPROCESSING_FILE", EXAMPLE_PREPROCESSING)

    client = TestClient(app, raise_server_exceptions=False)
    response = client.post("/api/v1/telemetry/assess", json={"latitude": 14.65, "longitude": 121.05})
    assert response.status_code == 200
    body = response.json()
    assert body["cyclone_assessment"]["status"] == "unavailable"
    assert body["rainfall_warning"]["status"]  # still there
    assert body["nearest_shelter"]["status"] == "available"


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


def test_repeated_class_name_is_rejected(tmp_path: Path) -> None:
    repeated = json.loads(EXAMPLE_PREPROCESSING.read_text(encoding="utf-8"))
    repeated["class_order"] = ["TD", "TS", "TS", "TY", "STY"]
    path = tmp_path / "preprocessing.json"
    path.write_text(json.dumps(repeated), encoding="utf-8")

    with pytest.raises(inference.ModelNotReady, match="exactly once"):
        inference.load_preprocessing(path)


def test_missing_weights_tell_you_where_to_put_them(tmp_path: Path) -> None:
    with pytest.raises(inference.ModelNotReady, match="Model file not found"):
        inference.load_session(tmp_path / "agap_tc_classifier.onnx")


@pytest.mark.skipif(
    not inference.model_path().exists(),
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
