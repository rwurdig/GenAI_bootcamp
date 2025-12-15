import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AppConfig:
    groq_api_key: Optional[str]
    openai_api_key: Optional[str]
    default_provider: str
    default_model: str
    default_temperature: float
    default_max_tokens: int


def load_config() -> AppConfig:
    return AppConfig(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        default_provider=os.getenv("DEFAULT_LLM_PROVIDER", "groq").strip().lower(),
        default_model=os.getenv("DEFAULT_LLM_MODEL", "llama-3.3-70b-versatile").strip(),
        default_temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0.2")),
        default_max_tokens=int(os.getenv("DEFAULT_MAX_TOKENS", "1024")),
    )
