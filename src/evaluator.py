from pydantic import ValidationError
from .models import (
        StudentSearchResults,
        RagDataset,
        MinimalSource,
        AnsweredQuestion
        )
from .errors import EvalError
from pathlib import Path
from tqdm import tqdm


_RECALL_K_LIST = [1, 3, 5, 10]


def display_recall(student_sources: Path, reference_sources: Path) -> None:
    """
    Given a student's sources and a ground-truth dataset,
    calculates the recall@k for each answered query.

    Arguments:
        student_sources - The path to the student's sources
        reference_sources - The path to the ground-truth sources

    Raises:
        EvalError - On invalid json formatting/file
    """
    try:
        student_model = StudentSearchResults.model_validate_json(
                student_sources.read_bytes())
        reference_model = RagDataset.model_validate_json(
                reference_sources.read_bytes())
    except ValidationError as e:
        raise EvalError(f"Invalid json model given: {e.errors}")
    else:
        reference_answered = [
                s for s in reference_model.rag_questions
                if isinstance(s, AnsweredQuestion)
                ]
        if not reference_answered:
            raise EvalError(
                    f"No AnsweredQuestion models found at path: {
                     reference_sources.as_posix()}")

        sources_by_id = {
                res.question_id: res.retrieved_sources
                for res in student_model.search_results
                }
        references_by_id = {
                res.question_id: res.sources
                for res in reference_answered
                }

        recall_at_k: dict[int, float] = {}
        for k in tqdm(_RECALL_K_LIST, desc="Calculating recall..."):
            valid_recall_len = 0
            for uuid, s in sources_by_id.items():
                try:
                    valid_recall_len += _is_valid_source(
                            s[:k], references_by_id[uuid][0])
                except Exception as e:
                    print(e)
                else:
                    recall_at_k[k] = (
                            valid_recall_len / len(references_by_id) * 100)

        print("\n\033[31m\x1b[1m===RECALL@K METRICS===\033[39m\n")
        print((
            f"\033[34mFound {len(sources_by_id)}/{len(references_by_id)} "
            "queries\033[39m\n"
               ))
        for k, v in recall_at_k.items():
            print(f"\033[30m> Recall@{k}\033[32m\t{v:.1f}%")


def _is_valid_source(
        student_sources: list[MinimalSource],
        reference_source: MinimalSource) -> bool:
    """
    Given `student_sources`,
    checks if both the file_path and character indices overlap with the
    `reference_source`

    Returns:
        bool - Whether it meets the overlap threshold
    """

    relevant_top_k = [
            p for p in student_sources if
            p.file_path == reference_source.file_path
            ]
    for source in relevant_top_k[:]:
        if not _get_iou_span(source, reference_source):
            relevant_top_k.remove(source)
    return True if relevant_top_k else False


def _get_iou_span(span_x: MinimalSource, span_y: MinimalSource) -> float:
    """
    Gets the intersection over union span of the 2 sources based on
    character indices.

    Returns:
        float - The overlap ranging from 0.0 - 1.0 with a minimum threshold of
            0.05.
    """    

    intersection_len = max(
            0,
            min(span_x.last_character_index, span_y.last_character_index) -
            max(span_x.first_character_index, span_y.first_character_index)
            )

    if not (union_len := (
        (span_x.last_character_index - span_x.first_character_index) +
        (span_y.last_character_index - span_y.first_character_index) -
        intersection_len
            )):
        return 0.0

    res = intersection_len / union_len
    return res if res > 0.05 else 0.0
