from src.errors import CLIError, EvalError
from src.cli import CLI
import pytest


_SEARCH_RESULTS_PATH = "tests/search_results/dataset_docs_public.json"
_DATASET_PATH = "tests/dataset/dataset_docs_public.json"


def test_evaluate_invalid_paths() -> None:
    with pytest.raises(CLIError):
        CLI().evaluate("a", _DATASET_PATH)

    with pytest.raises(CLIError):
        CLI().evaluate(_SEARCH_RESULTS_PATH, "a")


def test_evaluate_empty_search_results() -> None:
    with pytest.raises(EvalError):
        CLI().evaluate("tests/dummy_empty.json", _DATASET_PATH)


def test_evaluate_invalid_search_results() -> None:
    with pytest.raises(EvalError):
        CLI().evaluate("tests/dummy.json", _DATASET_PATH)


def test_evaluate_invalid_dataset() -> None:
    with pytest.raises(EvalError):
        CLI().evaluate(_SEARCH_RESULTS_PATH, "tests/dummy.json")
