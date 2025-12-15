from typing import List

from pydantic import BaseModel, Field


class MultipleChoiceQuestion(BaseModel):
    question: str = Field(..., min_length=5)
    options: List[str] = Field(..., min_length=2)
    answer: str = Field(..., min_length=1)


class OpenEndedQuestion(BaseModel):
    question: str = Field(..., min_length=5)
    answer: str = Field(..., min_length=1)


class MultipleChoiceQuiz(BaseModel):
    questions: List[MultipleChoiceQuestion]


class OpenEndedQuiz(BaseModel):
    questions: List[OpenEndedQuestion]
