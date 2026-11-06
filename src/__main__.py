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
            print(s.file_path, s.first_character_index, s.last_character_index)

    def search_dataset(
            self,
            dataset_path: Path,
            k: int,
            save_directory: str = "data/output/") -> None:
        ...

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
