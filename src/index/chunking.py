from langchain_text_splitters import MarkdownHeaderTextSplitter
from pydantic import BaseModel, Field
from pathlib import Path


class Chunk(BaseModel):
    start_index: int = Field(gt=0)
    end_index: int = Field(gt=0)
    text: str = Field(max_length=2000)


def chunk_file_markdown(path: Path) -> list[Chunk]:

    # with open(path.absolute()) as f:
    f = path.read_text()
    splitter = [("#", "Header 1"), ("#", "Header 2")]
    split = MarkdownHeaderTextSplitter(headers_to_split_on=splitter,
                                       strip_headers=False)
    text = split.split_text(f)
    print(text)
    return []


def chunk_file_python(path: Path) -> list[Chunk]:
    return []
