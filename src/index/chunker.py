from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from src import PROCESSED_CHUNKS_PATH, CHUNKED_FILES_NAME
from src.models import MinimalSource
from src.errors import IndexError
from pydantic import TypeAdapter
from pathlib import Path
from typing import Any
import json
import os


def create_chunks(path: Path, max_chunk_size: int) -> None:
    if not path.exists():
        raise IndexError((f"'{path}' doesn't exist.\n"
                          "Possible fixes: run the program from "
                          "the repository root or run make install "
                          "to extract the default corpus"))

    # TODO Add tqdm progress bar here
    chunks: bytes = _chunk_file_list([
        (list(path.rglob("*.py")),
         RecursiveCharacterTextSplitter.from_language(
             language=Language.PYTHON,
             chunk_size=max_chunk_size,
             chunk_overlap=max_chunk_size // 5)
         ),
        (list(path.rglob("*.md")),
         RecursiveCharacterTextSplitter.from_language(
             language=Language.MARKDOWN,
             chunk_size=max_chunk_size,
             chunk_overlap=max_chunk_size // 5)
         ),
        (list(path.rglob("*.txt")),
         RecursiveCharacterTextSplitter(
             chunk_size=max_chunk_size,
             chunk_overlap=max_chunk_size // 5)
         ),
        ])
    Path(PROCESSED_CHUNKS_PATH).mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_CHUNKS_PATH + CHUNKED_FILES_NAME, "wb") as f:
        f.write(chunks)


def _chunk_file_list(
        to_split: list[tuple[list[Path], RecursiveCharacterTextSplitter]],
        ) -> bytes:
    chunks: list[MinimalSource] = []
    adapter = TypeAdapter(list[MinimalSource])

    cache: list[dict[str, Any]] = []
    cache_file: Path = Path(PROCESSED_CHUNKS_PATH + CHUNKED_FILES_NAME)
    modified_files: set[Path] = set()

    if os.path.exists(cache_file):
        cache = json.load(cache_file.open())
        for i in cache:
            if os.path.getmtime(i["file_path"]) > i["last_index_time"]:
                modified_files.add(Path(i["file_path"]))
                cache = [k for k in cache if k is not i]
        chunks = adapter.validate_python(cache)
        if not modified_files:
            return adapter.dump_json(chunks, indent=2)

    for path_list, splitter in to_split:
        if cache:
            if modified_files.intersection(path_list):
                path_list = list(modified_files)
            else:
                continue
        for f in path_list:
            text = f.read_text()
            for chunk in splitter.split_text(text):
                start_index, end_index = (text.find(chunk), len(chunk))
                if start_index < 0 or end_index < start_index:
                    continue
                chunks.append(
                        MinimalSource(
                            file_path=f.as_posix(), content=chunk,
                            first_character_index=start_index,
                            last_character_index=end_index,
                            last_index_time=os.path.getmtime(f))
                        )
    return adapter.dump_json(chunks, indent=2)
