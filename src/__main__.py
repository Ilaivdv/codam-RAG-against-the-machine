from src.index import (
        create_chunks,
        init_retriever,
        retrieve_sources_from_query
        )
from src.errors import ChunkError, SearchError
from .constants import RAW_DATA_PATH
from .models import MinimalSource
from pathlib import Path
from bm25s import BM25
import fire
import sys


class CLI(object):
    def index(self, max_chunk_size: int) -> None:
        if max_chunk_size < 0 or max_chunk_size > 2000:
            raise ValueError(f"invalid max_chunk_size '{max_chunk_size}'")
        create_chunks(Path(RAW_DATA_PATH), max_chunk_size)

    def _search_from_query(self,
                           query: str,
                           k: int,
                           retriever: BM25) -> list[MinimalSource]:
        return retrieve_sources_from_query(query, k, retriever)

    def search(self, query: str, k: int) -> None:
        if k < 0:
            raise ValueError(f"Value '{k}' is invalid")
        if not query:
            raise ValueError("Query can't be empty")

        res: list[MinimalSource] = self._search_from_query(
                query, k, init_retriever())
        for s in res:
            print((f"{s.file_path} [{s.first_character_index}:"
                   f"{s.last_character_index}]"))

    def search_dataset(
            self,
            dataset_path: str,
            k: int,
            save_directory: str = "data/output/") -> None:
        if not Path(dataset_path).is_file() or not dataset_path.endswith(
                ".json"):
            raise ValueError((f"Input path '{save_directory}' is invalid, "
                              " expected file path"))
        if k < 0:
            raise ValueError(f"Value '{k}' is invalid")
        if save_directory.endswith("/"):
            raise ValueError((f"Output path '{save_directory}' is invalid, "
                              " expected file but got directory"))
        if Path(save_directory).exists():
            reply = input("WARNING: save_directory already " +
                          "exists, overwrite it? [y/n]: ").lower()
            if not (reply == "y" or reply == "yes" or not reply):
                sys.exit(1)
        print("ok")

    def answer(self, query: str, k: int) -> None:
        ...

    def answer_dataset(
            self,
            student_search_results_path: Path,
            save_directory: str) -> None:
        ...

    def evaluate(
            self,
            student_search_results_path: Path,
            dataset_path: str) -> None:
        ...


if __name__ == "__main__":
    try:
        fire.Fire(CLI)
    except (ValueError, ChunkError, SearchError) as e:
        print(e)
