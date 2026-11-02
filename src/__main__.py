from pathlib import Path
import fire


def index(max_chunk_size: int) -> None:
    from .index.chunking import chunk_file_markdown
    chunk_file_markdown(Path("data/raw/vllm-0.10.1/README.md"))


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
