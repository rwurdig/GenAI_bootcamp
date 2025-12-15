from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class LLMProviderCatalog:
    providers: List[str]
    models_by_provider: Dict[str, List[str]]


CATALOG = LLMProviderCatalog(
    providers=["groq", "openai"],
    models_by_provider={
        "groq": [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
        "openai": [
            "gpt-5",
            "gpt-4o",
            "gpt-4o-mini",
        ],
    },
)
