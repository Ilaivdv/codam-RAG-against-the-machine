from pydantic import BaseModel, Field


class Chunk(BaseModel):
    start_index: int = Field(gt=0)
    end_index: int = Field(gt=start_index)
    text: str = Field(max_length=2000)
