from pydantic import BaseModel, Field
import uuid


class MinimalSource(BaseModel):
    """
    A retrieved source for the RAG pipeline

    Attributes:
        file_path - Path of the source
        content - The content within the first- and last_character_index
        first_character_index - The file's starting index of the chunk
        last_character_index - The file's end index of the chunk
    """

    file_path: str
    content: str = Field(default="")
    first_character_index: int
    last_character_index: int
    last_index_time: float = Field(default=0.0)

    def __repr__(self) -> str:
        return (f"{self.file_path} [{self.first_character_index}:"
                f"{self.last_character_index}]")

    def __str__(self) -> str:
        return self.__repr__()


class UnansweredQuestion(BaseModel):
    """ An unanswered query holding the query and its uuid. """

    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """
    An answered query holding the `UnansweredQuestion` and the sources with
    the generated answers.
    """

    sources: list[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """ A model holding a list of either answered or unanswered queries. """

    rag_questions: list[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    """ A model holding a query with its top-k retrieved sources. """

    question_id: str
    question: str
    retrieved_sources: list[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """ A model extending `MinimalSearchResults` with the generated answer. """

    answer: str


class StudentSearchResults(BaseModel):
    """ A model holding search results from a dataset. """

    search_results: list[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """ A model extending `StudentSearchResults` with a generated answer. """

    search_results: list[MinimalAnswer]
    k: int
