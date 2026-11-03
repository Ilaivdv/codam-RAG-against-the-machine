from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_core.documents import Document
from src.models import MinimalSource
from src.errors import IngestError
from pathlib import Path


def chunk_file(path: Path) -> list[MinimalSource]:
    if not path.exists():
        raise IngestError(f"ERROR: {path} is not a valid file path")
    py_list: list[Path] = list(path.rglob("*.py"))
    txt_list: list[Path] = list(path.rglob("*.txt")) + list(path.rglob("*.md"))
    return []
