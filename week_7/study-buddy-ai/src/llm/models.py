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
            "llama-3.1-8b-instant",
            # Keep this list minimal; Groq model availability changes over time.
        ],
        "openai": [
            "gpt-5",
            "gpt-5.1",
            "gpt-5.2",
            "gpt-4o",
            "gpt-4o-mini",
        ],
    },
)
