"""Blog state models for LangGraph workflow"""
from typing import Optional, TypedDict

from pydantic import BaseModel, Field


class Blog(BaseModel):
    """Blog post model"""

    title: str = Field(description="Blog title")
    content: str = Field(description="Blog content in Markdown")
    language: str = Field(default="English", description="Language")


class BlogState(TypedDict):
    """State passed through the graph"""

    topic: str
    language: str
    blog: Optional[Blog]
    error: Optional[str]
