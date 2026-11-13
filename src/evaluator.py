from .models import StudentSearchResults, RagDataset, MinimalSource
from pydantic import ValidationError
from .errors import EvalError
from pathlib import Path


def display_recall(student_sources: Path, reference_sources: Path) -> None:
    try:
        student_model = StudentSearchResults.model_validate_json(
                student_sources.read_bytes())
        reference_model = RagDataset.model_validate_json(
                reference_sources.read_bytes())
    except ValidationError as e:
        raise EvalError(f"Invalid json model given: {e.errors}")
    else:
        recall = _get_iou_span(
                _get_overlapping_sources(student_model, reference_model),
                reference_model
                )
        print(recall)


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

    return intersection_len / union_len


def _get_overlapping_sources(
        student_sources: StudentSearchResults,
        reference_sources: RagDataset
        ) -> list[MinimalSource]:
    for s in StudentSearchResults.search_results:
        s.retrieved_sources
