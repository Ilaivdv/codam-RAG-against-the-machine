from src.errors import CLIError
from src.cli import CLI
import pytest


def test_index_negative_chunk_size() -> None:
    with pytest.raises(CLIError):
        CLI().index(-1)


def test_index_chunk_size_too_large() -> None:
    with pytest.raises(CLIError):
        CLI().index(2001)
