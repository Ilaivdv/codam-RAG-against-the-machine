from pydantic import BaseModel, Field
import uuid


class MinimalSource(BaseModel):
    file_path: str
    content: str
    first_character_index: int
    last_character_index: int
    last_index_time: float

    def __repr__(self) -> str:
        return (f"{self.file_path} [{self.first_character_index}:"
                f"{self.last_character_index}]")

    def __str__(self) -> str:
        return self.__repr__()


class UnansweredQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    sources: list[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    rag_questions: list[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    question_id: str
    question: str
    retrieved_sources: list[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    answer: str


class StudentSearchResults(BaseModel):
    search_results: list[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    search_results: list[MinimalAnswer]
    k: int
