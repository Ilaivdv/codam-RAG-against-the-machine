from .constants import RAW_DATA_PATH, PROCESSED_CHUNKS_PATH
from .models import (
        MinimalSource,
        MinimalAnswer,
        StudentSearchResults,
        StudentSearchResultsAndAnswer
        )
from .retriever import (
        init_retriever,
        retrieve_sources_from_query,
        retrieve_sources_from_dataset
        )
from .evaluator import display_recall
from pydantic import ValidationError
from .chunker import create_chunks
from .errors import CLIError
from .llm_model import LLM
from pathlib import Path
import os


_llm: LLM | None = None


class CLI:
    """ CLI class to handle argument parsing using fire. """

    def index(self, max_chunk_size: int) -> None:
        """ Ingest data/raw/ and build the index under data/processed/. """

        if not isinstance(max_chunk_size, int) or not \
                0 < max_chunk_size <= 2000:
            raise CLIError(("Expected integer value max_chunk_size "
                            f"between 1 and 2000, got: {max_chunk_size}"))

        create_chunks(Path(RAW_DATA_PATH), max_chunk_size)
        print(f"\n\033[32mSuccesfully indexed the corpus to {RAW_DATA_PATH +
              PROCESSED_CHUNKS_PATH}")

    def search(self, query: str, k: int) -> list[MinimalSource]:
        """ Return the top-k sources for a single query. """

        self._validate_k(k)
        if not query:
            raise CLIError("Got an empty query")
        res: list[MinimalSource] = retrieve_sources_from_query(
                query, k, init_retriever())
        return res

    def search_dataset(
            self,
            dataset_path: str,
            k: int,
            save_directory: str
            ) -> None:
        """
        Run search over a whole dataset and write a
        StudentSearchResults JSON file.
        """

        dataset_path = str(dataset_path)
        save_directory = str(save_directory)
        self._validate_json_path(dataset_path, "dataset_path")
        self._validate_k(k)
        self._validate_save_directory(save_directory)

        search_result = StudentSearchResults(
                search_results=retrieve_sources_from_dataset(
                    dataset_path=dataset_path,
                    k=k,
                    retriever=init_retriever()
                    ),
                k=k)
        file_dest: str = os.path.join(
                save_directory, os.path.split(dataset_path)[1])
        Path(save_directory).mkdir(parents=True, exist_ok=True)
        with open(file_dest, "wb") as f:
            f.write(search_result.model_dump_json(indent=2).encode())
        print(f"\n\033[32mSuccesfully written search results to {file_dest}")

    def answer(self, query: str, k: int) -> str:
        """ Answer a single query using the retrieved context. """

        if not query:
            raise CLIError("Got an empty query")
        self._validate_k(k)

        res: list[MinimalSource] = retrieve_sources_from_query(
                query, k, init_retriever())

        global _llm
        if _llm is None:
            _llm = LLM("Qwen/Qwen3-0.6B")

        return _llm.answer_prompt(query, res)

    def answer_dataset(
            self,
            student_search_results_path: str,
            save_directory: str) -> None:
        """
        Generate answers for a dataset, producing a
        StudentSearchResultsAndAnswer JSON file.
        """

        student_search_results_path = str(student_search_results_path)
        save_directory = str(save_directory)
        self._validate_json_path(student_search_results_path,
                                 "student_search_results_path")
        self._validate_save_directory(save_directory)

        try:
            search_results = StudentSearchResults.model_validate_json(
                    Path(student_search_results_path).read_bytes())
        except ValidationError:
            raise CLIError(
                    f"Got invalid student_search_results_path: {
                    student_search_results_path}")

        answers: list[MinimalAnswer] = []
        for res in search_results.search_results:
            answers.append(MinimalAnswer(
                question_id=res.question_id,
                question=res.question,
                retrieved_sources=res.retrieved_sources,
                answer=self.answer(res.question, search_results.k)
                ))

        results_and_answers = StudentSearchResultsAndAnswer(
                search_results=answers,
                k=search_results.k
                )
        file_dest: str = os.path.join(
                save_directory, os.path.split(student_search_results_path)[1])
        Path(save_directory).mkdir(parents=True, exist_ok=True)
        with open(file_dest, "wb") as f:
            f.write(results_and_answers.model_dump_json(indent=2).encode())
        print(f"\n\033[32mSuccesfully wrote all generated answers under {
              save_directory}")

    def evaluate(
            self,
            student_search_results_path: str,
            dataset_path: str) -> None:
        """ Reports a recall@k against a ground-truth dataset. """
        self._validate_json_path(dataset_path, "student_search_results_path")
        self._validate_json_path(dataset_path, "dataset_path")

        display_recall(Path(student_search_results_path), Path(dataset_path))

    def _validate_k(self, k: int) -> None:
        """ Validates k value and raises `CLIError` on invalid k or k < 1. """

        if not isinstance(k, int) or k <= 0:
            raise CLIError(("Expected an integer greater "
                            f"than 0 for argument k, got: {k}"))

    def _validate_json_path(self, path: str, var_name: str) -> None:
        """ Takes `path` and raises `CLIError` on invalid json file path. """

        if not os.path.isfile(path) or not \
                path.endswith(".json"):
            raise CLIError(("Expected an existing JSON file "
                            f"path for {var_name}, got: {path}"))

    def _validate_save_directory(self, save_directory: str) -> None:
        """ Takes `save_directory` and raises `CLIError` on invalid path. """

        if save_directory.startswith(("/", "~", "../")):
            raise CLIError(("Argument save_directory out of scope, "
                            f"got: {save_directory}"))
