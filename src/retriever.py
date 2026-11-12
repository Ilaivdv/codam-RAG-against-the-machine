from .models import (
        MinimalSource,
        MinimalSearchResults,
        RagDataset,
        AnsweredQuestion,
        UnansweredQuestion
        )
from .constants import PROCESSED_CHUNKS_PATH, CHUNKED_FILES_NAME
from pydantic import ValidationError
from .errors import SearchError
from pathlib import Path
from typing import Any
from tqdm import tqdm
import bm25s
import json


def init_retriever() -> bm25s.BM25:
    corpus_path: Path = Path(PROCESSED_CHUNKS_PATH + CHUNKED_FILES_NAME)
    if not corpus_path.exists():
        raise SearchError(("Corpus not initialized! "
                           "Please run `uv run -m src index --k=<int>` first"))

    corpus: list[dict[str, Any]] = json.load(corpus_path.open())
    corpus_tokens = bm25s.tokenize([chunk["content"] for chunk in corpus if
                                    chunk.get("content")])

    retriever: bm25s.BM25 = bm25s.BM25(corpus=corpus)
    retriever.index(corpus_tokens)
    return retriever


def retrieve_sources_from_query(
        query: str,
        k: int,
        retriever: bm25s.BM25
        ) -> list[MinimalSource]:
    sources_list: list[MinimalSource] = []
    query_tokens = bm25s.tokenize(query, show_progress=False)
    results = retriever.retrieve(
            query_tokens=query_tokens, k=k,
            n_threads=-1)[0]

    for i in range(results.shape[1]):
        doc = results[0, i]
        sources_list.append(MinimalSource(**doc))

    return sources_list


def retrieve_sources_from_dataset(
        k: int,
        dataset_path: str,
        retriever: bm25s.BM25
        ) -> list[MinimalSearchResults]:
    query_list: list[AnsweredQuestion | UnansweredQuestion] | None = []
    query_retrievals: list[MinimalSearchResults] = []
    with open(dataset_path, "rb") as f:
        json_dict: dict[str, Any] = json.load(f)
        try:
            query_list = RagDataset.model_validate(json_dict).rag_questions
        except ValidationError:
            raise SearchError(("Expected JSON list 'rag_questions' "
                               f"at file path: {dataset_path}"))
        for query in tqdm(query_list, desc="Creating MinimalSearchResults"):
            query_retrievals.append(MinimalSearchResults(
                question_id=query.question_id,
                question=query.question,
                retrieved_sources=retrieve_sources_from_query(
                    query.question, k, retriever
                    )
                ))
    return query_retrievals
