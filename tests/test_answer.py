from src.errors import CLIError
from src.cli import CLI
import pytest


def test_answer_empty_query() -> None:
    with pytest.raises(CLIError):
        CLI().answer("", 5)


def test_answer_negative_k() -> None:
    with pytest.raises(CLIError):
        CLI().search("hi", -5)


def test_answer_non_int_k() -> None:
    with pytest.raises(CLIError):
        CLI().search("hi", "boo")  # type: ignore


def test_invalid_answer_dataset_path() -> None:
    with pytest.raises(CLIError):
        CLI().answer_dataset("hi", "data/output")

    with pytest.raises(CLIError):
        CLI().answer_dataset("hi.json", "data/output")


def test_invalid_answer_save_directory() -> None:
    with pytest.raises(CLIError):
        CLI().answer_dataset("tests/dummy.json", "/fake_directory")

    with pytest.raises(CLIError):
        CLI().answer_dataset("tests/dummy.json", "~/fake_directory")

    with pytest.raises(CLIError):
        CLI().answer_dataset("tests/dummy.json", "../fake_directory")


def test_empty_dataset_json() -> None:
    with pytest.raises(CLIError):
        CLI().answer_dataset("tests/dummy_empty.json", "data")
