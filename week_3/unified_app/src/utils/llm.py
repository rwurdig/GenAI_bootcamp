import os
import ssl
from typing import Literal, Optional

from dotenv import load_dotenv

# LangChain llms
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_groq import ChatGroq

load_dotenv()

# Optional SSL relax (dev only)
if os.getenv("SSL_VERIFY", "true").lower() == "false":
    try:
        ssl._create_default_https_context = ssl._create_unverified_context  # type: ignore
    except Exception:
        pass

Provider = Literal["openai", "groq", "aimlapi", "auto"]
EmbProvider = Literal["openai"]

def get_llm(provider: Provider = "auto",
            model: Optional[str] = None,
            temperature: float = 0.1,
            api_key: Optional[str] = None):
    """Return a LangChain chat model for the chosen provider.

    - openai: uses ChatOpenAI with OpenAI API
    - groq: uses ChatGroq with Groq API
    - aimlapi: uses ChatOpenAI with AIMLAPI base URL
    - auto: defaults to "openai"
    
    Args:
        provider: The LLM provider to use
        model: Optional model name (provider-specific)
        temperature: Sampling temperature (0.0-1.0)
        api_key: Optional API key override (uses env var if not provided)
    """
    if provider == "auto":
        provider = "openai"

    if provider == "openai":
        openai_key = api_key or os.getenv("OPENAI_API_KEY", "").strip()
        if not openai_key:
            raise ValueError("OPENAI_API_KEY is required for the OpenAI provider.")
        
        return ChatOpenAI(
            api_key=openai_key,
            model=model or "gpt-4o-mini",
            temperature=temperature,
            timeout=120,
        )
    
    elif provider == "groq":
        groq_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        if not groq_key:
            raise ValueError("GROQ_API_KEY is required for the Groq provider.")
        
        return ChatGroq(
            api_key=groq_key,
            model=model or "llama-3.3-70b-versatile",
            temperature=temperature,
            timeout=120,
        )
    
    elif provider == "aimlapi":
        aimlapi_key = api_key or os.getenv("AIMLAPI_API_KEY", "").strip()
        if not aimlapi_key:
            raise ValueError("AIMLAPI_API_KEY is required for the AIMLAPI provider.")
        
        return ChatOpenAI(
            api_key=aimlapi_key,
            base_url="https://api.aimlapi.com/v1",
            model=model or "gpt-4o-mini",
            temperature=temperature,
            timeout=120,
        )

    raise ValueError(f"Unknown provider: {provider}")

def get_embeddings(provider: EmbProvider = None, model: Optional[str] = None):
    provider = provider or os.getenv("EMBEDDINGS_PROVIDER", "openai")  # type: ignore
    if provider != "openai":
        raise ValueError("Only the OpenAI embeddings provider is supported. Set EMBEDDINGS_PROVIDER=openai.")

    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not openai_key:
        raise ValueError("OPENAI_API_KEY is required for embeddings when using the OpenAI/AIMLAPI provider.")

    return OpenAIEmbeddings(
        api_key=openai_key,
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        model=model or os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-small"),
    )