from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class FaqSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query must not be empty")
        return value


class FaqSearchResult(BaseModel):
    id: str
    slug: str
    question: str
    answer: str
    score: float


class FaqSearchResponse(BaseModel):
    found: bool
    results: list[FaqSearchResult]


class FaqCreate(BaseModel):
    slug: str = Field(..., min_length=1, max_length=128)
    category: str = Field(..., min_length=1, max_length=64)
    question: str = Field(..., min_length=1, max_length=4000)
    answer: str = Field(..., min_length=1, max_length=8000)


class FaqUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=128)
    category: str | None = Field(default=None, min_length=1, max_length=64)
    question: str | None = Field(default=None, min_length=1, max_length=4000)
    answer: str | None = Field(default=None, min_length=1, max_length=8000)


class FaqItemOut(BaseModel):
    id: str
    slug: str
    category: str
    question: str
    answer: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
