from .models import MinimalSource, MinimalSearchResults, StudentSearchResults
from .errors import SearchError, ChunkError
from .constants import RAW_DATA_PATH
from src.index import (
        create_chunks,
        init_retriever,
        retrieve_sources_from_query
        )
from pathlib import Path
from bm25s import BM25
from typing import Any
import json
import fire
import os


class CLI:
    def index(self, max_chunk_size: int) -> None:
        if not isinstance(max_chunk_size, int) or not \
                0 < max_chunk_size <= 2000:
            raise ChunkError(("Expected integer value max_chunk_size "
                              f"between 0 and 2000, got: {max_chunk_size}"))
        create_chunks(Path(RAW_DATA_PATH), max_chunk_size)

    def search(self, query: str, k: int) -> None:
        if not isinstance(k, int) or k <= 0:
            raise SearchError(("Expected an integer greater "
                               f"than 0 for argument k, got: {k}"))
        res: list[MinimalSource] = retrieve_sources_from_query(
                query, k, init_retriever())
        for s in res:
            print((f"{s.file_path} [{s.first_character_index}:"
                   f"{s.last_character_index}]"))

    def search_dataset(
            self,
            dataset_path: str,
            k: int,
            save_directory: str
            ) -> None:
        if not os.path.isfile(dataset_path) or not \
                dataset_path.endswith(".json"):
            raise SearchError(("Expected an existing JSON file "
                               f"for dataset_path, got: {dataset_path}"))
        if not isinstance(k, int) or k <= 0:
            raise SearchError(("Expected an integer greater "
                               f"than 0 for argument k, got: {k}"))
        if save_directory.startswith(("/", "~")):
            raise SearchError(("Argument save_directory out of scope, "
                               f"got: {save_directory}"))

        query_list: list[dict[str, str]] | None = []
        query_retrievals: list[MinimalSearchResults] = []
        retriever: BM25 = init_retriever()
        with open(dataset_path, "rb") as f:
            json_dict: dict[str, Any] = json.load(f)
            if not (query_list := json_dict.get("rag_questions")):
                raise SearchError(("Expected JSON list 'rag_questions' "
                                   f"at file path: {dataset_path}"))
            for query in query_list:
                query_retrievals.append(MinimalSearchResults(
                    question_id=query["question_id"],
                    question=query["question"],
                    retrieved_sources=retrieve_sources_from_query(
                        query["question"], k, retriever
                        )
                    ))
        search_result = StudentSearchResults(
                search_results=query_retrievals,
                k=k)
        file_dest: str = os.path.join(
                save_directory, os.path.split(dataset_path)[1])
        with open(file_dest, "wb") as f:
            f.write(search_result.model_dump_json(indent=2).encode())

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
    except (ChunkError, SearchError) as e:
        print(e)
