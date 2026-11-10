from json import JSONDecodeError
from src.errors import CLIError
from src.cli import CLI
import pytest


def test_index_negative_chunk_size() -> None:
    with pytest.raises(CLIError):
        assert CLI().index(-1)


def test_index_chunk_size_too_large() -> None:
    with pytest.raises(CLIError):
        assert CLI().index(2001)


def test_search_empty_query() -> None:
    with pytest.raises(CLIError):
        assert CLI().search("", 5)


def test_search_negative_k() -> None:
    with pytest.raises(CLIError):
        assert CLI().search("hi", -5)


def test_invalid_search_dataset_path() -> None:
    with pytest.raises(CLIError):
        assert CLI().search_dataset("hi", 5, "data/output")

    with pytest.raises(CLIError):
        assert CLI().search_dataset("hi.json", 5, "data/output")


def test_search_dataset_negative_k() -> None:
    with pytest.raises(CLIError):
        assert CLI().search_dataset("tests/dummy.json", -5, "data/")


def test_invalid_search_dataset_save_directory() -> None:
    with pytest.raises(CLIError):
        assert CLI().search_dataset("tests/dummy.json", 5, "/fake_directory")

    with pytest.raises(CLIError):
        assert CLI().search_dataset("tests/dummy.json", 5, "~/fake_directory")


def test_empty_dataset_json() -> None:
    with pytest.raises(JSONDecodeError):
        assert CLI().search_dataset("tests/dummy_empty.json", 5, "data")


def test_invalid_dataset_json_key() -> None:
    with pytest.raises(CLIError, match=r".* JSON .*"):
        assert CLI().search_dataset("tests/dummy.json", 5, "data")
