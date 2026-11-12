from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from .constants import PROCESSED_CHUNKS_PATH, CHUNKED_FILES_NAME
from pydantic import TypeAdapter, ValidationError
from .models import MinimalSource
from .errors import IndexError
from pathlib import Path
from typing import Any
from tqdm import tqdm
import json
import os


def create_chunks(path: Path, max_chunk_size: int) -> None:
    """
    Splits files into .py files and a groups .txt and .md files.
    Initializes `RecursiveCharacterTextSplitter` with the equivalent language
    and gives it to `_chunk_file_list` to write the results to a file path
    defined in `src/constants.py`.


    Arguments:
        path - Directory to parse all files from
        max_chunk_size - Max size a files chunk can be

    Raises:
        IndexError - On invalid path or uninitialized corpus
    """

    if not path.exists():
        raise IndexError((f"'{path}' doesn't exist.\n"
                          "Possible fixes: run the program from "
                          "the repository root or run make install "
                          "to extract the default corpus"))

    chunks: bytes = _chunk_file_list([
        (list(path.rglob("*.py")),
         RecursiveCharacterTextSplitter.from_language(
             language=Language.PYTHON,
             chunk_size=max_chunk_size,
             chunk_overlap=max_chunk_size // 3)
         ),
        (list(path.rglob("*.txt")) + list(path.rglob("*.md")),
         RecursiveCharacterTextSplitter(
             chunk_size=max_chunk_size,
             chunk_overlap=max_chunk_size // 3)
         ),
        ])
    Path(PROCESSED_CHUNKS_PATH).mkdir(parents=True, exist_ok=True)
    with open(PROCESSED_CHUNKS_PATH + CHUNKED_FILES_NAME, "wb") as f:
        f.write(chunks)


def _chunk_file_list(
        to_split: list[tuple[list[Path], RecursiveCharacterTextSplitter]],
        ) -> bytes:
    """
    Splits given file lists into chunks using the paired
    `RecursiveCharacterTextSplitter` and makes sure everything follows
    the json schema defined in `src/models.py`.
    
    The built in caching decreases indexing time majorly on small changes.
    When a missing file path is found in the corpus, it will re-index to
    ensure a valid and safe output.


    Arguments:
        to_split - A list of tuple pairs containing file paths of one type with
            it's equivalent splitter
    
    Returns:
        bytes - The json representation of a list of MinimalSource models
    """

    chunks: list[MinimalSource] = []
    adapter = TypeAdapter(list[MinimalSource])

    cache: list[dict[str, Any]] = []
    cache_file: Path = Path(PROCESSED_CHUNKS_PATH + CHUNKED_FILES_NAME)
    modified_files: set[Path] = set()

    if os.path.exists(cache_file):
        cache = json.load(cache_file.open())
        file_changed: bool = False
        for i in tqdm(cache[:], desc="Parsing cache", colour="blue"):
            if not i.get("file_path") or not \
                    os.path.exists(str(i.get("file_path"))):
                tqdm.write(("\033[33mWARNING: Found chunk with missing/invalid"
                            " file_path, rebuilding the corpus\033[39m"))
                cache.clear()
                break
            try:
                MinimalSource.model_validate(i)
                if os.path.getmtime(i["file_path"]) > i["last_index_time"]:
                    file_changed = True
            except ValidationError:
                file_changed = True
            if file_changed:
                modified_files.add(Path(i["file_path"]))
                cache.remove(i)
                file_changed = False
        chunks = adapter.validate_python(cache)
        if not modified_files and cache:
            return adapter.dump_json(chunks, indent=2)

    for path_list, splitter in to_split:
        if cache:
            if modified_files.intersection(path_list):
                path_list = list(modified_files)
            else:
                continue
        progress_bar = tqdm(path_list, colour="blue", leave=False)
        for f in progress_bar:
            progress_bar.set_description(f"Chunking file: {f.name}")
            text = f.read_text()
            for chunk in splitter.split_text(text):
                start_index = text.find(chunk)
                end_index = start_index + len(chunk)
                if start_index < 0 or start_index > end_index:
                    continue
                chunks.append(
                        MinimalSource(
                            file_path=f.as_posix(), content=chunk,
                            first_character_index=start_index,
                            last_character_index=end_index,
                            last_index_time=os.path.getmtime(f))
                        )
    return adapter.dump_json(chunks, indent=2)
