from .models import StudentSearchResults, RagDataset, MinimalSource
from pathlib import Path


def display_recall(student_sources: Path, reference_sources: Path) -> ...:
    ...


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
