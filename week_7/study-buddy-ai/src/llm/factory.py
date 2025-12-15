from src.config import AppConfig


def build_llm(
    cfg: AppConfig,
    provider: str,
    model: str,
    temperature: float,
    max_tokens: int,
):
    provider = provider.strip().lower()
    model = (model or "").strip()

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

        # Some OpenAI models (notably gpt-5*) only support the default temperature (=1).
        # We hard-force it to 1.0 to prevent 400 errors when the UI slider differs.
        effective_temperature = 1.0 if model.startswith("gpt-5") else float(temperature)

        base_kwargs = {"model": model, "max_tokens": max_tokens, "temperature": effective_temperature}

        try:
            return ChatOpenAI(api_key=cfg.openai_api_key, **base_kwargs)
        except TypeError:
            return ChatOpenAI(openai_api_key=cfg.openai_api_key, **base_kwargs)

    raise ValueError(f"Unsupported provider: {provider}")
