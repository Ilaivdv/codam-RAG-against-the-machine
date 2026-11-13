from pydantic import ValidationError
from .models import (
        StudentSearchResults,
        RagDataset,
        MinimalSource,
        AnsweredQuestion
        )
from .errors import EvalError
from pathlib import Path


_RECALL_K_LIST = [1, 3, 5, 10]


def display_recall(student_sources: Path, reference_sources: Path) -> None:
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
            # print(reference_model)
            print(reference_answered)
            raise EvalError(
                    f"No AnsweredQuestion models found in dataset_path")

        sources_by_id = {
                res.question_id: res.retrieved_sources
                for res in student_model.search_results
                }
        references_by_id = {
                res.question_id: res.sources
                for res in reference_answered
                }

        for k in _RECALL_K_LIST:
            for uuid in references_by_id.keys():
                try:
                    recall_list = [
                            _get_recall_at_k(set(student), set(reference))
                            for student, reference in zip(
                                sources_by_id.get(uuid),
                                references_by_id.get(uuid))
                            ]
                    print(recall_list)
                except Exception:
                    pass
        # recall = _get_iou_span(student_model, reference_model)
        # print(recall)


def _get_recall_at_k(
        student_sources: set[MinimalSource],
        reference_sources: set[MinimalSource]) -> float:
    student_paths = set([p.file_path for p in student_sources])
    reference_paths = set([p.file_path for p in reference_sources])

    relevant_top_k = student_paths & reference_paths
    for source in list(relevant_top_k):
        if not _get_iou_span(
                next((
                    s for s in student_sources if s.file_path == source
                    ), None),
                next((
                    s for s in reference_sources if s.file_path == source
                    ), None)
                ):
            relevant_top_k.remove(source)
    return len(relevant_top_k) / len(reference_sources)


def _get_iou_span(span_x: MinimalSource, span_y: MinimalSource) -> float:
    intersection_len = max(
            0,
            min(span_x.last_character_index, span_y.last_character_index) -
            max(span_x.first_character_index, span_y.first_character_index)
            )

    if union_len := (
            (span_x.last_character_index - span_x.first_character_index) +
            (span_y.last_character_index - span_y.first_character_index) -
            intersection_len
            ) == 0:
        return 0.0

    res = intersection_len / union_len
    return res if res > 0.05 else 0
