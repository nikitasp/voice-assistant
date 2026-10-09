import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

_TRAILING_PUNCT = re.compile(r"[\s\?\.\!\,\;\:]+$")


class UnansweredCreate(BaseModel):
    question: str = Field(..., min_length=1)

    @field_validator("question")
    @classmethod
    def question_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("question must not be empty")
        normalized = _TRAILING_PUNCT.sub("", stripped.lower()).strip()
        if not normalized:
            raise ValueError("question must not be empty")
        return value


class UnansweredOut(BaseModel):
    id: str
    question: str
    frequency: int
    first_asked_at: datetime
    last_asked_at: datetime
    status: str

    model_config = {"from_attributes": True}


class UnansweredConvertRequest(BaseModel):
    category: str = Field(..., min_length=1, max_length=64)
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    slug: str | None = Field(default=None, min_length=1, max_length=128)
