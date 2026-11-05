from src import PROCESSED_CHUNKS_PATH, CHUNKED_FILES_NAME
from src.errors import SearchError
from pathlib import Path
from typing import Any
import bm25s
import json


def build_index_from_corpus() -> bm25s.BM25:
    corpus_path: Path = Path(PROCESSED_CHUNKS_PATH + CHUNKED_FILES_NAME)
    if not corpus_path.exists():
        raise SearchError(("Corpus not initialized! "
                           "Please run `index` command first"))

    corpus: list[dict[str, Any]] = json.load(corpus_path.open())
    corpus_tokens = bm25s.tokenize([chunk["content"] for chunk in corpus])

    retriever: bm25s.BM25 = bm25s.BM25(corpus=corpus)
    retriever.index(corpus_tokens)
    return retriever


def retrieve_sources_from_query(
        query: str,
        k: int,
        retriever: bm25s.BM25
        ) -> ...:
    query_tokens = bm25s.tokenize(query)
    res, scores = retriever.retrieve(query_tokens=query_tokens, k=k,
                                     n_threads=-1)

    for i in range(res.shape[1]):
        doc, score = res[0, i], scores[0, i]
        print(f"Path {doc["file_path"]} (score: {score:.2f}): {doc[
              "first_character_index"],
              doc["last_character_index"]}")
