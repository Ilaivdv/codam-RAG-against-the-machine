from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_core.documents import Document
from collections.abc import Iterator
from ..errors import IngestError
from pydantic import Field
from pathlib import Path


class Chunk(Document):
    start_index: int = Field(gt=0)
    end_index: int = Field(gt=0)


def chunk_file(path: Path) -> list[Chunk]:
    if not path.exists():
        raise IngestError(f"ERROR: {path} is not a valid file path")
    py_list: Iterator[Path] = path.rglob("*.py")
    # txt_list:
    return []
