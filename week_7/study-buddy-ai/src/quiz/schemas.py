from typing import List

from pydantic import BaseModel, Field


class MCQQuestion(BaseModel):
    question: str = Field(..., min_length=5)
    options: List[str] = Field(..., min_length=2)
    answer: str


class OpenQuestion(BaseModel):
    question: str = Field(..., min_length=5)
    answer: str


class MCQQuiz(BaseModel):
    questions: List[MCQQuestion]


class OpenQuiz(BaseModel):
    questions: List[OpenQuestion]
