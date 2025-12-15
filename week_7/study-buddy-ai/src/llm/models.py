# available providers and their models
# update this when groq/openai add new ones

PROVIDERS = ["groq", "openai"]

MODELS = {
    "groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ],
    "openai": [
        "gpt-5",
        "gpt-5.1",
        "gpt-5.2",
        "gpt-4o",
        "gpt-4o-mini",
    ],
}


class LLMCatalog:
    """Simple catalog for UI dropdowns"""

    providers = PROVIDERS
    models_by_provider = MODELS


CATALOG = LLMCatalog()
