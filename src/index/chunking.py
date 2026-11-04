from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
# from langchain_core.documents import Document
from src.models import MinimalSource
from src.errors import IngestError
from pathlib import Path
import pickle


def create_pickled_chunks(path: Path,
                          max_chunk_size: int) -> list[MinimalSource]:
    if not path.exists():
        raise IngestError(f"{path} is not a valid file path")

    # TODO Add tqdm progress bar here
    chunks: list[MinimalSource] = (
            _chunk_py_files(list(path.rglob("*.py")), max_chunk_size) +
            _chunk_txt_files(
                list(path.rglob("*.txt")) + list(path.rglob("*.md")),
                max_chunk_size))

    return []


def _chunk_py_files(file_path_list: list[Path],
                    max_chunk_size: int) -> list[MinimalSource]:
    splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,
            chunk_size=max_chunk_size,
            chunk_overlap=200,
            )
    chunks: list[MinimalSource] = []
    for f in file_path_list:
        text = f.read_text()
        for chunk in splitter.split_text(text):
            start_index, end_index = (text.find(chunk), len(chunk))
            if start_index < 0:
                continue
            chunks.append(
                    MinimalSource(
                        file_path=f.as_posix(), content=chunk,
                        first_character_index=start_index,
                        last_character_index=end_index)
                    )
    return chunks


def _chunk_txt_files(file_path_list: list[Path],
                     max_chunk_size: int) -> list[MinimalSource]:
    splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_chunk_size,
            chunk_overlap=200,
            add_start_index=True,
            )
    chunks: list[MinimalSource] = []
    for f in file_path_list:
        text = f.read_text()
        for chunk in splitter.split_text(text):
            start_index, end_index = (text.find(chunk), len(chunk))
            if start_index < 0:
                continue
            chunks.append(
                    MinimalSource(
                        file_path=f.as_posix(), content=chunk,
                        first_character_index=start_index,
                        last_character_index=end_index)
                    )
    return chunks
