"""Groq LLM provider"""
from __future__ import annotations

import os

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


class LLMProvider:
    """Unified LLM provider supporting Groq and OpenAI"""

    def __init__(self, provider: str = "groq", model: str | None = None, api_key: str | None = None):
        self.provider = provider.lower()

        if self.provider == "groq":
            key = api_key or os.getenv("GROQ_API_KEY")
            if not key:
                raise ValueError("GROQ_API_KEY not found. Add it to .env or pass explicitly.")
            self.llm = ChatGroq(
                api_key=key,
                model=model or "llama-3.3-70b-versatile",
                temperature=0.7,
            )
        else:  # openai
            key = api_key or os.getenv("OPENAI_API_KEY")
            if not key:
                raise ValueError("OPENAI_API_KEY not found. Add it to .env or pass explicitly.")
            self.llm = ChatOpenAI(
                api_key=key,
                model=model or "gpt-4o-mini",
                temperature=0.7,
            )

    def get_llm(self):
        return self.llm
