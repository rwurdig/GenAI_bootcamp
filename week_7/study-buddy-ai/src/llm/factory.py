from src.config import AppConfig


def _is_model_deprecated(err: Exception) -> bool:
    """groq keeps deprecating models, check if that's the error"""
    msg = str(err).lower()
    return "model_decommissioned" in msg or "has been decommissioned" in msg


def _get_available_groq_models(api_key: str) -> list[str]:
    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        resp = client.models.list()
        return [m.id for m in getattr(resp, "data", []) if getattr(m, "id", None)]
    except Exception:
        return []


def _fallback_groq_model(api_key: str) -> str:
    # these are the ones that usually work
    preferred = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
    available = set(_get_available_groq_models(api_key))

    for m in preferred:
        if not available or m in available:
            return m
    return preferred[0]


def build_llm(cfg: AppConfig, provider: str, model: str, temperature: float, max_tokens: int):
    provider = provider.strip().lower()
    model = (model or "").strip()

    # groq deprecated these - map to working ones
    if provider == "groq":
        deprecated = {
            "mixtral-8x7b-32768": "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile": "llama-3.3-70b-versatile",
            "gemma2-9b-it": "llama-3.3-70b-versatile",
        }
        model = deprecated.get(model, model)

    if provider == "groq":
        from langchain_groq import ChatGroq

        if not cfg.groq_api_key:
            raise ValueError("GROQ_API_KEY missing - set env var or k8s secret")

        def _make_groq(model_name):
            # langchain-groq changed param names between versions
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
            return _make_groq(model)
        except Exception as e:
            if _is_model_deprecated(e):
                return _make_groq(_fallback_groq_model(cfg.groq_api_key))
            raise

    elif provider == "openai":
        from langchain_openai import ChatOpenAI

        if not cfg.openai_api_key:
            raise ValueError("OPENAI_API_KEY missing - set env var or k8s secret")

        # gpt-5 only allows temperature=1, others are fine
        temp = 1.0 if model.startswith("gpt-5") else float(temperature)

        try:
            return ChatOpenAI(
                api_key=cfg.openai_api_key,
                model=model,
                max_tokens=max_tokens,
                temperature=temp,
            )
        except TypeError:
            return ChatOpenAI(
                openai_api_key=cfg.openai_api_key,
                model=model,
                max_tokens=max_tokens,
                temperature=temp,
            )

    raise ValueError(f"Unknown provider: {provider}")
