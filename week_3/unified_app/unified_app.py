
import os
import tempfile
from typing import Dict, List

import streamlit as st
from dotenv import load_dotenv

from src.rag.indexer import build_or_update_index
from src.rag.qa import ask as rag_ask
from src.summarizers.news import summarize_article_text
from src.summarizers.youtube import process_youtube, qa_over_documents
from src.utils.audio import tts_elevenlabs, transcribe_audio
from src.utils.news import fetch_article

load_dotenv()

st.set_page_config(
    page_title="Week 3 · AI Content Suite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- Session defaults ----------------
def _init_session_state():
    """Initialize session state with environment variables and track sources"""
    defaults: Dict[str, object] = {
        "news_summary": None,
        "news_meta": None,
        "yt_summary": None,
        "yt_vector": None,
        "yt_chat": [],
        "voice_vector": None,
        "voice_chat": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Initialize API keys from environment if not already in session
    if "openai_api_key" not in st.session_state:
        st.session_state["openai_api_key"] = os.getenv("OPENAI_API_KEY", "")
    if "groq_api_key" not in st.session_state:
        st.session_state["groq_api_key"] = os.getenv("GROQ_API_KEY", "")
    if "aimlapi_api_key" not in st.session_state:
        st.session_state["aimlapi_api_key"] = os.getenv("AIMLAPI_API_KEY", "")
    if "elevenlabs_api_key" not in st.session_state:
        st.session_state["elevenlabs_api_key"] = os.getenv("ELEVEN_LABS_API_KEY", "")
    if "openai_base_url" not in st.session_state:
        st.session_state["openai_base_url"] = os.getenv("OPENAI_BASE_URL", "")
    if "embeddings_model" not in st.session_state:
        st.session_state["embeddings_model"] = os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-small")
    
    # Track which keys came from environment
    if "keys_from_env" not in st.session_state:
        st.session_state["keys_from_env"] = {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "groq": bool(os.getenv("GROQ_API_KEY")),
            "aimlapi": bool(os.getenv("AIMLAPI_API_KEY")),
            "elevenlabs": bool(os.getenv("ELEVEN_LABS_API_KEY")),
        }


def _clear_youtube_state():
    st.session_state["yt_summary"] = None
    st.session_state["yt_vector"] = None
    st.session_state["yt_chat"] = []


def _clear_voice_state():
    st.session_state["voice_vector"] = None
    st.session_state["voice_chat"] = []


def _require_openai_key(api_key: str) -> bool:
    if not api_key:
        st.warning("Please provide an OpenAI API key in the sidebar to continue.")
        return False
    return True


_init_session_state()

# ---------------- Sidebar configuration ----------------
st.sidebar.header("⚙️ Configuration")

# API Key Management Section
with st.sidebar.expander("🔑 Manage API Keys", expanded=False):
    # Show environment variable status
    env_keys = st.session_state.get("keys_from_env", {})
    loaded_from_env = [k.upper() for k, v in env_keys.items() if v]
    if loaded_from_env:
        st.info(f"✓ Loaded from .env: {', '.join(loaded_from_env)}")
    
    st.caption("Enter API keys below. Fields left empty will preserve existing values.")
    
    openai_input = st.text_input(
        "OpenAI API Key",
        type="password",
        value=st.session_state.get("openai_api_key", ""),
        key="openai_input",
        help="Required for all LLM and embedding calls"
    )
    
    groq_input = st.text_input(
        "Groq API Key",
        type="password",
        value=st.session_state.get("groq_api_key", ""),
        key="groq_input",
        help="Optional: for Groq models"
    )
    
    aimlapi_input = st.text_input(
        "AIMLAPI Key",
        type="password",
        value=st.session_state.get("aimlapi_api_key", ""),
        key="aimlapi_input",
        help="Optional: for AIMLAPI proxy"
    )
    
    elevenlabs_input = st.text_input(
        "ElevenLabs API Key",
        type="password",
        value=st.session_state.get("elevenlabs_api_key", ""),
        key="elevenlabs_input",
        help="Optional: for text-to-speech"
    )
    
    if st.button("💾 Save Keys", type="primary", use_container_width=True):
        # Smart update: only change non-empty values
        if openai_input.strip():
            st.session_state["openai_api_key"] = openai_input.strip()
        if groq_input.strip():
            st.session_state["groq_api_key"] = groq_input.strip()
        if aimlapi_input.strip():
            st.session_state["aimlapi_api_key"] = aimlapi_input.strip()
        if elevenlabs_input.strip():
            st.session_state["elevenlabs_api_key"] = elevenlabs_input.strip()
        st.success("✓ Keys saved to session")
        st.rerun()

st.sidebar.divider()

# Pull keys from session state
openai_api_key = st.session_state.get("openai_api_key", "")
groq_api_key = st.session_state.get("groq_api_key", "")
aimlapi_api_key = st.session_state.get("aimlapi_api_key", "")
elevenlabs_api_key = st.session_state.get("elevenlabs_api_key", "")

# Model and configuration settings
st.sidebar.subheader("Model Settings")

openai_base_url = st.sidebar.text_input(
    "OpenAI Base URL",
    value=st.session_state.get("openai_base_url", ""),
    help="Leave empty for api.openai.com. Set for OpenAI-compatible proxies.",
)
if openai_base_url.strip():
    st.session_state["openai_base_url"] = openai_base_url.strip()

embeddings_model = st.sidebar.text_input(
    "Embeddings Model",
    value=st.session_state.get("embeddings_model", "text-embedding-3-small"),
    help="Used for vector store creation (Voice RAG & YouTube Q&A).",
)
if embeddings_model.strip():
    st.session_state["embeddings_model"] = embeddings_model.strip()

# Provider selection
provider_choice = st.sidebar.selectbox(
    "Provider",
    options=["openai", "groq", "aimlapi"],
    index=0,
    help="Select LLM provider (requires corresponding API key)"
)

# Model selection based on provider
model_options = {
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-5"],
    "groq": ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"],
    "aimlapi": ["gpt-4o-mini", "gpt-4o", "claude-3-5-sonnet-20241022", "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo", "mistralai/Mistral-7B-Instruct-v0.3"]
}

model_choice = st.sidebar.selectbox(
    "Chat Model",
    options=model_options.get(provider_choice, ["gpt-4o-mini"]),
    index=0,
    help=f"Available models for {provider_choice}"
)

# Allow advanced users to type a custom model string which will override the selectbox
custom_model = st.sidebar.text_input(
    "Custom model (optional)",
    value="",
    help="Enter a custom model name (e.g. gpt-5 or my-org/custom-model) to override the selection."
)

# Final model used by calls: prefer custom_model when provided
model_final = custom_model.strip() or model_choice

model_temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.1,
    step=0.1,
)

st.sidebar.divider()

# FFmpeg location for YouTube audio processing
st.sidebar.subheader("🎬 YouTube Audio Settings")

# Default FFmpeg location
default_ffmpeg = r"C:\ffmpeg-bin\bin\ffmpeg.exe"
ffmpeg_location = st.sidebar.text_input(
    "FFmpeg Location (optional)",
    value=st.session_state.get("ffmpeg_location", os.getenv("FFMPEG_LOCATION", default_ffmpeg)),
    key="ffmpeg_input",
    help="Path to ffmpeg binary or bin directory. Defaults to C:\\ffmpeg-bin\\bin\\ffmpeg.exe",
    placeholder=default_ffmpeg
)

# Always set the ffmpeg location (use default if empty)
ffmpeg_path = ffmpeg_location.strip() or default_ffmpeg
st.session_state["ffmpeg_location"] = ffmpeg_path
os.environ["FFMPEG_LOCATION"] = ffmpeg_path

# Verify if ffmpeg exists at the specified location
if os.path.exists(ffmpeg_path):
    st.sidebar.success(f"✓ FFmpeg: {ffmpeg_path}")
elif os.path.exists(os.path.dirname(ffmpeg_path)):
    # Check if directory exists (for dir path instead of exe path)
    ffmpeg_dir = os.path.dirname(ffmpeg_path) if ffmpeg_path.endswith('.exe') else ffmpeg_path
    if os.path.exists(os.path.join(ffmpeg_dir, "ffmpeg.exe")):
        st.sidebar.success(f"✓ FFmpeg: {ffmpeg_dir}")
    else:
        st.sidebar.warning(f"⚠️ FFmpeg not found at: {ffmpeg_path}")
else:
    # Check if ffmpeg is on PATH as fallback
    try:
        import subprocess
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            st.sidebar.info("✓ FFmpeg found on system PATH")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        st.sidebar.warning(f"⚠️ FFmpeg not found at: {ffmpeg_path}")

st.sidebar.divider()

# Status indicators
st.sidebar.caption("**API Key Status:**")
col1, col2 = st.sidebar.columns(2)
with col1:
    openai_status = "🟢 Active" if openai_api_key else "🔴 Missing"
    st.caption(f"OpenAI: {openai_status}")
    groq_status = "🟢 Active" if groq_api_key else "🔴 Missing"
    st.caption(f"Groq: {groq_status}")
with col2:
    aiml_status = "🟢 Active" if aimlapi_api_key else "🔴 Missing"
    st.caption(f"AIMLAPI: {aiml_status}")
    eleven_status = "🟢 Active" if elevenlabs_api_key else "🔴 Missing"
    st.caption(f"ElevenLabs: {eleven_status}")

st.sidebar.divider()
st.sidebar.caption("Built for the Andela GenAI Bootcamp · Week 3")

# Apply configuration to environment for downstream libs
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
if openai_base_url:
    os.environ["OPENAI_BASE_URL"] = openai_base_url
else:
    os.environ.pop("OPENAI_BASE_URL", None)
os.environ["EMBEDDINGS_MODEL"] = embeddings_model

# ---------------- Hero section ----------------
st.title("🤖 Week 3 · Unified AI Content Suite")
st.markdown(
    """
    Three production-ready assistants in one Streamlit experience:

    1. **News Article Summarizer** – scrape, chunk, and synthesize articles.
    2. **YouTube Summarizer & Q&A** – transcribe videos, summarize, and chat over their content.
    3. **Voice RAG Assistant** – ingest your docs, ask by text or upload audio, and receive grounded answers (with optional TTS).

    Configure credentials and preferences from the sidebar, then explore each tab below.
    """
)

# ---------------- Tabs ----------------
news_tab, youtube_tab, voice_tab = st.tabs([
    "📰 News Summarizer",
    "🎥 YouTube Summarizer + Q&A",
    "🎙️ Voice Assistant RAG",
])

# ---------------- Tab 1: News Summarizer ----------------
with news_tab:
    st.header("📰 News Article Summarizer")
    st.write("Summarize any article using LangChain's map-reduce pipeline.")

    col_url, col_style = st.columns([2, 1])
    with col_url:
        article_url = st.text_input(
            "Article URL",
            placeholder="https://example.com/news-story",
        )
    with col_style:
        style_label = st.selectbox(
            "Summary Style",
            options=["Detailed", "Concise", "Bullets"],
        )

    style_value = style_label.lower()

    if st.button("Summarize Article", type="primary"):
        if not _require_openai_key(openai_api_key):
            pass
        elif not article_url:
            st.warning("Please enter a valid article URL.")
        else:
            with st.spinner("Fetching article content..."):
                article_text = fetch_article(article_url)
            if not article_text:
                st.error("Could not fetch content from the provided URL.")
            else:
                # Set API key for chosen provider
                if provider_choice == "openai":
                    os.environ["OPENAI_API_KEY"] = openai_api_key
                elif provider_choice == "groq":
                    os.environ["GROQ_API_KEY"] = groq_api_key
                elif provider_choice == "aimlapi":
                    os.environ["AIMLAPI_API_KEY"] = aimlapi_api_key
                
                with st.spinner("Summarizing article..."):
                    result = summarize_article_text(
                        text=article_text,
                        provider=provider_choice,
                        model=model_final,
                        style=style_value,
                        temperature=model_temperature,
                    )
                st.session_state["news_summary"] = result["summary"]
                st.session_state["news_meta"] = {
                    "chunks": result["chunks"],
                    "style": style_label,
                }

    if st.session_state.get("news_summary"):
        st.subheader("Summary")
        st.markdown(st.session_state["news_summary"])
        meta = st.session_state.get("news_meta", {})
        st.caption(
            f"Chunks processed: {meta.get('chunks', '?')} · Style: {meta.get('style', style_label)}"
        )

# ---------------- Tab 2: YouTube Summarizer ----------------
with youtube_tab:
    st.header("🎥 YouTube Summarizer & Conversational Q&A")
    st.write("Process YouTube videos end-to-end: transcript, summary, vector store, and chat.")

    col_url, col_style = st.columns([2, 1])
    with col_url:
        youtube_url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
        )
    with col_style:
        yt_style_label = st.selectbox(
            "Summary Style",
            options=["Detailed", "Concise", "Bullets"],
            key="yt_style",
        )
    yt_style_value = yt_style_label.lower()

    if st.button("Process Video", type="primary"):
        if not _require_openai_key(openai_api_key):
            pass
        elif not youtube_url:
            st.warning("Please enter a valid YouTube URL.")
        else:
            try:
                # Set API keys for chosen provider
                if provider_choice == "openai":
                    os.environ["OPENAI_API_KEY"] = openai_api_key
                elif provider_choice == "groq":
                    os.environ["GROQ_API_KEY"] = groq_api_key
                elif provider_choice == "aimlapi":
                    os.environ["AIMLAPI_API_KEY"] = aimlapi_api_key
                
                # Ensure ffmpeg location is set if provided
                if st.session_state.get("ffmpeg_location"):
                    os.environ["FFMPEG_LOCATION"] = st.session_state["ffmpeg_location"]
                
                with st.spinner("Processing video: transcript → summary → vector store..."):
                    result = process_youtube(
                        url=youtube_url,
                        provider=provider_choice,
                        model=model_final,
                        embeddings_provider="openai",
                        temperature=model_temperature,
                        persist_dir=".chroma/video",
                    )
            except Exception as exc:
                st.error(f"Video processing failed: {exc}")
                _clear_youtube_state()
            else:
                st.session_state["yt_summary"] = result["summary"]
                st.session_state["yt_vector"] = result["vector"]
                st.session_state["yt_chat"] = []
                st.success(
                    f"Transcript characters: {result['transcript_chars']} · Chunks: {result['chunks']}"
                )

    if st.session_state.get("yt_summary"):
        st.subheader("Video Summary")
        st.markdown(st.session_state["yt_summary"])

    st.divider()
    st.subheader("Ask About the Video")

    if st.session_state.get("yt_chat"):
        for message in st.session_state["yt_chat"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    video_question = st.chat_input("Ask a question about the processed video...")
    if video_question:
        if not _require_openai_key(openai_api_key):
            pass
        elif not st.session_state.get("yt_vector"):
            st.warning("Please process a video first.")
        else:
            # Set API keys for chosen provider
            if provider_choice == "openai":
                os.environ["OPENAI_API_KEY"] = openai_api_key
            elif provider_choice == "groq":
                os.environ["GROQ_API_KEY"] = groq_api_key
            elif provider_choice == "aimlapi":
                os.environ["AIMLAPI_API_KEY"] = aimlapi_api_key
            
            st.session_state["yt_chat"].append({"role": "user", "content": video_question})
            with st.chat_message("assistant"):
                with st.spinner("Retrieving and answering..."):
                    answer = qa_over_documents(
                        vect=st.session_state["yt_vector"],
                        question=video_question,
                        provider=provider_choice,
                        model=model_final,
                        temperature=model_temperature,
                    )
                    st.markdown(answer)
            st.session_state["yt_chat"].append({"role": "assistant", "content": answer})

    if st.button("Clear Video Session"):
        _clear_youtube_state()
        st.experimental_rerun()

# ---------------- Tab 3: Voice Assistant RAG ----------------
with voice_tab:
    st.header("🎙️ Voice-Enabled RAG Assistant")
    st.write("Upload documents, build a vector index, and query by typing or audio upload.")

    persist_dir = ".chroma/voice"
    uploaded_files = st.file_uploader(
        "Upload PDF / TXT / MD files",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
    )

    if st.button("Build / Update Knowledge Base", type="primary"):
        if not _require_openai_key(openai_api_key):
            pass
        elif not uploaded_files:
            st.warning("Please upload at least one document.")
        else:
            tmp_paths: List[str] = []
            for file in uploaded_files:
                tmp_path = os.path.join(tempfile.gettempdir(), file.name)
                with open(tmp_path, "wb") as handle:
                    handle.write(file.getbuffer())
                tmp_paths.append(tmp_path)
            try:
                with st.spinner("Creating vector store from documents..."):
                    vect = build_or_update_index(
                        files=tmp_paths,
                        persist_dir=persist_dir,
                        embeddings_provider="openai",
                    )
            except Exception as exc:
                st.error(f"Vector store build failed: {exc}")
                _clear_voice_state()
            else:
                st.session_state["voice_vector"] = vect
                st.session_state["voice_chat"] = []
                st.success("Knowledge base ready.")

    st.divider()
    st.subheader("Ask Your Knowledge Base")

    interaction_mode = st.radio(
        "Question Input",
        options=["Type", "Upload audio"],
        horizontal=True,
    )

    user_question = ""
    if interaction_mode == "Type":
        user_question = st.text_input("Type your question")
    else:
        audio_upload = st.file_uploader(
            "Upload short audio (wav/mp3)",
            type=["wav", "mp3"],
            key="voice_audio",
        )
        if audio_upload is not None:
            tmp_audio = os.path.join(tempfile.gettempdir(), audio_upload.name)
            with open(tmp_audio, "wb") as temp_audio:
                temp_audio.write(audio_upload.read())
            with st.spinner("Transcribing audio with Whisper..."):
                user_question = transcribe_audio(tmp_audio)
            st.info(f"Transcribed: {user_question}")

    if st.button("Ask Knowledge Base"):
        if not _require_openai_key(openai_api_key):
            pass
        elif not st.session_state.get("voice_vector"):
            st.warning("Please build the knowledge base first.")
        elif not user_question:
            st.warning("Please provide a question (typed or transcribed).")
        else:
            # Set API keys for chosen provider
            if provider_choice == "openai":
                os.environ["OPENAI_API_KEY"] = openai_api_key
            elif provider_choice == "groq":
                os.environ["GROQ_API_KEY"] = groq_api_key
            elif provider_choice == "aimlapi":
                os.environ["AIMLAPI_API_KEY"] = aimlapi_api_key
            
            with st.spinner("Generating grounded answer..."):
                answer = rag_ask(
                    vect=st.session_state["voice_vector"],
                    question=user_question,
                    provider=provider_choice,
                    model=model_final,
                    temperature=model_temperature,
                )
            st.session_state["voice_chat"].append({"role": "user", "content": user_question})
            st.session_state["voice_chat"].append({"role": "assistant", "content": answer})
            st.markdown(answer)

            if st.checkbox("🔊 Play answer with ElevenLabs"):
                with st.spinner("Generating speech..."):
                    speech = tts_elevenlabs(answer)
                if speech:
                    st.audio(speech, format="audio/mp3")
                else:
                    st.warning("TTS unavailable. Ensure ELEVEN_LABS_API_KEY is configured.")

    if st.session_state.get("voice_chat"):
        st.divider()
        st.subheader("Conversation History")
        for message in st.session_state["voice_chat"]:
            role_label = "You" if message["role"] == "user" else "Assistant"
            st.markdown(f"**{role_label}:** {message['content']}")

    if st.button("Clear Voice Session"):
        _clear_voice_state()
        st.experimental_rerun()
