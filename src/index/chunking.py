from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from src.models import MinimalSource
from src.errors import ChunkError
from pydantic import TypeAdapter
from pathlib import Path
from typing import Any
import json
import os


_PROCESSED_CHUNKS_PATH = "data/processed/"


def create_chunks(path: Path,
                  max_chunk_size: int,
                  to_file: str = "processed_indices") -> None:
    if not path.exists():
        raise ChunkError((f"'{path}' is not a valid file path.\n"
                          "Possible fix: run the program from "
                          "the repository root."))
    if "." in to_file or "/" in to_file:
        raise ChunkError((f"'{to_file}' can't be a directory "
                          "or have a file extension"))

    # TODO Add tqdm progress bar here
    chunks: bytes = _chunk_file_list([
        (list(path.rglob("*.py")),
         RecursiveCharacterTextSplitter.from_language(
             language=Language.PYTHON,
             chunk_size=max_chunk_size,
             chunk_overlap=200)
         ),
        (list(path.rglob("*.md")) + list(path.rglob("*.txt")),
         RecursiveCharacterTextSplitter(
             chunk_size=max_chunk_size,
             chunk_overlap=200)
         )], to_file)
    Path(_PROCESSED_CHUNKS_PATH).mkdir(parents=True, exist_ok=True)
    with open(f"{_PROCESSED_CHUNKS_PATH}{to_file}.json", "wb") as f:
        f.write(chunks)


def _chunk_file_list(
        to_split: list[tuple[list[Path], RecursiveCharacterTextSplitter]],
        to_file: str,
        ) -> bytes:
    chunks: list[MinimalSource] = []
    adapter = TypeAdapter(list[MinimalSource])

    cache: list[dict[str, Any]] = []
    cache_file: Path = Path(f"{_PROCESSED_CHUNKS_PATH}{to_file}.json")
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
