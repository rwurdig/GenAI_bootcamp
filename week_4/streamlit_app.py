"""Streamlit UI for Blog Generator"""
from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from src.graphs.graph_builder import GraphBuilder
from src.llms.groq_llm import LLMProvider

load_dotenv()

st.set_page_config(page_title="AI Blog Generator", page_icon="✍️", layout="wide")

st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="main-header">✍️ AI Blog Generator</div>', unsafe_allow_html=True)

MODEL_OPTIONS = {
    "Groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ],
    "OpenAI": [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "gpt-5",
    ],
}

with st.sidebar:
    st.header("⚙️ Configuration")
    provider = st.selectbox("LLM Provider", list(MODEL_OPTIONS.keys()), index=0)

    selected_model = st.selectbox("Model", MODEL_OPTIONS[provider])

    language = st.selectbox("Language", ["English", "Spanish", "French", "Portuguese"])

    env_var = f"{provider.upper()}_API_KEY"
    env_api_key = os.getenv(env_var, "")
    if env_api_key:
        st.success(f"Using {provider} API key from .env ({env_var})")
        api_key_override = st.text_input("Override API key (optional)", type="password", value="")
    else:
        st.warning(f"No {provider} API key detected in .env. Please enter it below.")
        api_key_override = st.text_input(f"{provider} API Key", type="password", value="")

    effective_api_key = api_key_override.strip() or env_api_key


topic = st.text_area("Blog Topic", placeholder="Example: The Future of AI", height=100)

if st.button("🚀 Generate Blog", type="primary"):
    if not topic.strip():
        st.error("Please enter a blog topic")
    elif not effective_api_key:
        st.error(f"Please enter your {provider} API key")
    else:
        with st.spinner(f"Generating with {provider}..."):
            try:
                llm_provider = LLMProvider(provider=provider.lower(), model=selected_model, api_key=effective_api_key)
                llm = llm_provider.get_llm()

                graph_builder = GraphBuilder(llm)
                graph = graph_builder.build()

                result = graph.invoke({"topic": topic, "language": language, "blog": None, "error": None})

                if result.get("error"):
                    st.error(f"Error: {result['error']}")
                else:
                    blog = result["blog"]
                    st.success("✅ Blog generated!")
                    st.markdown(f"# {blog['title']}")
                    st.divider()
                    st.markdown(blog['content'])

                    md_content = f"# {blog['title']}\n\n{blog['content']}"
                    st.download_button(
                        "📥 Download Markdown",
                        data=md_content,
                        file_name=f"{blog['title'][:50]}.md",
                        mime="text/markdown",
                    )
            except Exception as exc:
                st.error(f"Error: {exc}")
