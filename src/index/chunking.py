from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
# from langchain_core.documents import Document
from src.models import MinimalSource
from src.errors import IngestError
from pathlib import Path
import pickle


def create_pickled_chunks(path: Path,
                          max_chunk_size: int) -> list[MinimalSource]:
    if not path.exists():
        raise IngestError(f"{path} is not a valid file path")

    # TODO Add tqdm progress bar here
    chunks: list[MinimalSource] = _chunk_file_list([
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
         ),
        ])
    print(chunks[0])
    return []


def _chunk_file_list(
        to_split: list[tuple[list[Path], RecursiveCharacterTextSplitter]]
        ) -> list[MinimalSource]:
    chunks: list[MinimalSource] = []
    for path_list, splitter in to_split:
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
                            last_character_index=end_index)
                        )
    return chunks
