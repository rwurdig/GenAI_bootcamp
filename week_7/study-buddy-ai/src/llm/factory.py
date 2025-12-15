from src.config import AppConfig


def _looks_like_groq_model_decommissioned(err: Exception) -> bool:
    msg = str(err).lower()
    return "model_decommissioned" in msg or "has been decommissioned" in msg


def _groq_list_available_models(api_key: str) -> list[str]:
    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        resp = client.models.list()
        # `resp.data` entries have an `id` field.
        return [m.id for m in getattr(resp, "data", []) if getattr(m, "id", None)]
    except Exception:
        return []


def _groq_pick_fallback_model(api_key: str) -> str:
    preferred = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ]
    available = set(_groq_list_available_models(api_key))
    for candidate in preferred:
        if not available or candidate in available:
            return candidate
    return preferred[0]


def build_llm(
    cfg: AppConfig,
    provider: str,
    model: str,
    temperature: float,
    max_tokens: int,
):
    provider = provider.strip().lower()
    model = (model or "").strip()

    # Handle known deprecations so older configs keep working.
    # Groq decommissioned several legacy models; map them to a supported default.
    if provider == "groq":
        deprecated_map = {
            "mixtral-8x7b-32768": "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile": "llama-3.3-70b-versatile",
            "gemma2-9b-it": "llama-3.3-70b-versatile",
        }
        model = deprecated_map.get(model, model)

    if provider == "groq":
        from langchain_groq import ChatGroq

        if not cfg.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY is missing. Set it as an environment variable or Kubernetes Secret."
            )

        def _construct(model_name: str):
            try:
                return ChatGroq(
                    api_key=cfg.groq_api_key,
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except TypeError:
                return ChatGroq(
                    groq_api_key=cfg.groq_api_key,
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

        try:
            return _construct(model)
        except Exception as e:
            if _looks_like_groq_model_decommissioned(e):
                fallback_model = _groq_pick_fallback_model(cfg.groq_api_key)
                return _construct(fallback_model)
            raise

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
