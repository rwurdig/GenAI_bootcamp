import os

from dotenv import load_dotenv


# TODO: maybe add pydantic Settings class later for validation


class AppConfig:
    """App configuration - reads from env vars"""

    def __init__(self):
        load_dotenv(override=False)

        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.default_provider = os.getenv("DEFAULT_LLM_PROVIDER", "groq").strip().lower()
        self.default_model = os.getenv("DEFAULT_LLM_MODEL", "llama-3.3-70b-versatile").strip()
        self.default_temperature = float(os.getenv("DEFAULT_TEMPERATURE", "0.2"))
        self.default_max_tokens = int(os.getenv("DEFAULT_MAX_TOKENS", "1024"))


def load_config() -> AppConfig:
    return AppConfig()
