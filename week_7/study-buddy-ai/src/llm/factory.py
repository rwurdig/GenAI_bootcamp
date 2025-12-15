from src.config import AppConfig


def build_llm(
    cfg: AppConfig,
    provider: str,
    model: str,
    temperature: float,
    max_tokens: int,
):
    provider = provider.strip().lower()

    if provider == "groq":
        from langchain_groq import ChatGroq

        if not cfg.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is missing. Set it as an environment variable or Kubernetes Secret."
            )

        try:
            return ChatGroq(
                api_key=cfg.groq_api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except TypeError:
            return ChatGroq(
                groq_api_key=cfg.groq_api_key,
                model_name=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        if not cfg.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is missing. Set it as an environment variable or Kubernetes Secret."
            )

        try:
            return ChatOpenAI(
                api_key=cfg.openai_api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except TypeError:
            return ChatOpenAI(
                openai_api_key=cfg.openai_api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    raise ValueError(f"Unsupported provider: {provider}")
