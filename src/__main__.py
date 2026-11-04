from .index.chunking import create_pickled_chunks
from pathlib import Path
import fire


_RAW_DATA_PATH = "data/raw/"


def index(max_chunk_size: int) -> None:
    create_pickled_chunks(Path(_RAW_DATA_PATH), max_chunk_size)


def search(query: str, k: int) -> None:
    ...


def search_dataset(
        dataset_path: Path,
        k: int,
        save_directory: str) -> None:
    ...


def answer(query: str, k: int) -> None:
    ...


def answer_dataset(
        student_search_results_path: Path,
        save_directory: str) -> None:
    ...


def evaluate(
        student_search_results_path: Path,
        dataset_path: str) -> None:
    ...


if __name__ == "__main__":
    fire.Fire()
