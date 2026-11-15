from src.errors import CLIError, SearchError
from src.cli import CLI
import pytest


def test_search_empty_query() -> None:
    with pytest.raises(CLIError):
        CLI().search("", 5)


def test_search_negative_k() -> None:
    with pytest.raises(CLIError):
        CLI().search("hi", -5)


def test_search_non_int_k() -> None:
    with pytest.raises(CLIError):
        CLI().search("hi", "a")  # type: ignore


def test_invalid_search_dataset_path() -> None:
    with pytest.raises(CLIError):
        CLI().search_dataset("hi", 5, "data/output")

    with pytest.raises(CLIError):
        CLI().search_dataset("hi.json", 5, "data/output")


def test_search_dataset_negative_k() -> None:
    with pytest.raises(CLIError):
        CLI().search_dataset("tests/dummy_query.json", -5, "data/")


def test_search_dataset_non_int_k() -> None:
    with pytest.raises(CLIError):
        CLI().search_dataset("tests/dummy.json", "hi", "data/")  # type: ignore


def test_invalid_search_dataset_save_directory() -> None:
    with pytest.raises(CLIError):
        CLI().search_dataset("tests/dummy.json", 5, "/fake_directory")

    with pytest.raises(CLIError):
        CLI().search_dataset("tests/dummy.json", 5, "~/fake_directory")

    with pytest.raises(CLIError):
        CLI().search_dataset("tests/dummy.json", 5, "../fake_directory")


def test_empty_dataset_json() -> None:
    with pytest.raises(SearchError):
        CLI().search_dataset("tests/dummy_empty.json", 5, "data")


def test_invalid_dataset_json_key() -> None:
    with pytest.raises(SearchError, match=r".* JSON .*"):
        CLI().search_dataset("tests/dummy.json", 5, "data")
