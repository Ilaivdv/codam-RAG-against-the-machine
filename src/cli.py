from .models import MinimalSource, MinimalSearchResults, StudentSearchResults
from .retriever import (
        init_retriever,
        retrieve_sources_from_query,
        retrieve_sources_from_dataset
        )
from .constants import RAW_DATA_PATH
from .chunker import create_chunks
from .errors import CLIError
from .llm_model import LLM
from pathlib import Path
from bm25s import BM25
from typing import Any
import json
import os


class CLI:
    def index(self, max_chunk_size: int) -> None:
        if not isinstance(max_chunk_size, int) or not \
                0 < max_chunk_size <= 2000:
            raise CLIError(("Expected integer value max_chunk_size "
                            f"between 0 and 2000, got: {max_chunk_size}"))
        create_chunks(Path(RAW_DATA_PATH), max_chunk_size)

    def search(self, query: str, k: int) -> None:
        if not isinstance(k, int) or k <= 0:
            raise CLIError(("Expected an integer greater "
                            f"than 0 for argument k, got: {k}"))
        if not query:
            raise CLIError("Got an empty query")
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
            raise CLIError(("Expected an existing JSON file "
                            f"for dataset_path, got: {dataset_path}"))
        if not isinstance(k, int) or k <= 0:
            raise CLIError(("Expected an integer greater "
                            f"than 0 for argument k, got: {k}"))
        if save_directory.startswith(("/", "~", "../")):
            raise CLIError(("Argument save_directory out of scope, "
                            f"got: {save_directory}"))

        search_result = StudentSearchResults(
                search_results=retrieve_sources_from_dataset(
                    k=k,
                    dataset_path=dataset_path,
                    retriever=init_retriever()
                    ),
                k=k)
        file_dest: str = os.path.join(
                save_directory, os.path.split(dataset_path)[1])
        with open(file_dest, "wb") as f:
            f.write(search_result.model_dump_json(indent=2).encode())

    def answer(self, query: str, k: int) -> None:
        if not isinstance(k, int) or k <= 0:
            raise CLIError(("Expected an integer greater "
                            f"than 0 for argument k, got: {k}"))
        if not query:
            raise CLIError("Got an empty query")
        res: list[MinimalSource] = retrieve_sources_from_query(
                query, k, init_retriever())
        llm = LLM("Qwen/Qwen3-0.6B")
        print(llm.process_prompt(query, res))

    def answer_dataset(
            self,
            student_search_results_path: str,
            save_directory: str) -> None:
        if not os.path.isfile(student_search_results_path) or not \
                student_search_results_path.endswith(".json"):
            raise CLIError(("Expected an existing JSON file "
                            "for student_search_results_path, "
                            f"got: {student_search_results_path}"))
        if save_directory.startswith(("/", "~", "../")):
            raise CLIError(("Argument save_directory out of scope, "
                            f"got: {save_directory}"))

    def evaluate(
            self,
            student_search_results_path: str,
            dataset_path: str) -> None:
        ...
