"""
Streamlit Frontend for Groq + OpenAI LLM Application
Supports both Groq (Llama) and OpenAI (GPT-5) models with automatic provider switching
"""
import streamlit as st
from main import LLMApp
import os

# Page configuration
st.set_page_config(
    page_title="Simple LLM Chat Application (Groq + OpenAI)",
    page_icon="🤖",
    layout="centered"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "llm_app" not in st.session_state:
    st.session_state.llm_app = None
if "last_config" not in st.session_state:
    st.session_state.last_config = {}

# Title and description
st.title("🤖 Groq + OpenAI LLM Chat Application")
st.markdown(
    """
    Chat with open-source models via Groq or OpenAI's GPT models. 
    Enter your API keys in the sidebar to get started.
    
    - **Groq keys**: [console.groq.com](https://console.groq.com)
    - **OpenAI keys**: [platform.openai.com](https://platform.openai.com)
    """
)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API keys (optional if present in .env)
    groq_api_key = st.text_input(
        "Groq API Key", 
        type="password", 
        help="Optional if GROQ_API_KEY is set in .env"
    )
    if not groq_api_key:
        groq_api_key = os.getenv("GROQ_API_KEY", "")

    openai_api_key = st.text_input(
        "OpenAI API Key", 
        type="password", 
        help="Optional if OPENAI_API_KEY is set in .env"
    )
    if not openai_api_key:
        openai_api_key = os.getenv("OPENAI_API_KEY", "")

    st.divider()
    
    # Model selection
    model = st.selectbox(
        "Model",
        [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-120b",
            "gpt-5",
            "gpt-5-mini",
            "gpt-5-nano",
        ],
        help="Choose your preferred AI model"
    )
    st.divider()
    
    # Chatbot persona
    chatbot_name = st.text_input(
        "Chatbot name",
        value="Thoth",
        help="Give your assistant a name/identity"
    )

    system_prompt = st.text_area(
        "System prompt (optional)",
        value="",
        help="Set behavior and instructions for the assistant"
    )

    st.divider()

    # Model parameters
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Controls randomness: lower = more focused, higher = more creative"
    )

    max_tokens = st.slider(
        "Max Tokens",
        min_value=256,
        max_value=2048,
        value=1024,
        step=256,
        help="Maximum length of the response (uses max_completion_tokens for GPT-5)"
    )

    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True, type="primary"):
        st.session_state.messages = []
        if st.session_state.llm_app:
            st.session_state.llm_app.clear_history()
        st.rerun()


def _pick_api_key(model_name: str) -> str | None:
    """Return correct API key based on model/provider"""
    if model_name.startswith("gpt-") or model_name.startswith("openai/"):
        return openai_api_key or None
    return groq_api_key or None


# Configuration tracking for reinitializing the app
current_config = {
    "model": model,
    "chatbot_name": chatbot_name.strip(),
    "system_prompt": (system_prompt or "").strip(),
}


def _needs_reinit(prev: dict, curr: dict) -> bool:
    """Check if app needs to be reinitialized"""
    if not prev:
        return True
    # Re-init if model/provider OR persona fields changed
    return any(prev.get(k) != curr.get(k) for k in ["model", "chatbot_name", "system_prompt"])


# (Re)initialize the app if configuration changed
if _needs_reinit(st.session_state.last_config, current_config) or st.session_state.llm_app is None:
    key = _pick_api_key(model)
    try:
        st.session_state.llm_app = LLMApp(
            api_key=key,
            model=model,
            chatbot_name=current_config["chatbot_name"] or "Thoth",
            default_system_prompt=(current_config["system_prompt"] or None),
        )
        st.session_state.last_config = current_config
        # Clear history when changing persona/model to avoid context mixing
        st.session_state.messages = []
    except Exception as e:
        st.error(f"❌ Error initializing LLM App: {str(e)}")
        st.info("💡 Please check your API keys and try again.")
        st.stop()


# Display provider and model information
provider = "OpenAI" if model.startswith("gpt-") else "Groq"
col1, col2 = st.columns(2)
with col1:
    st.caption(f"**Provider:** {provider}")
with col2:
    st.caption(f"**Model:** {model}")

st.divider()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Validate API key for chosen provider
    active_key = _pick_api_key(model)
    if not active_key:
        st.warning("⚠️ Please enter a valid API key for the selected provider in the sidebar (.env also supported).")
    else:
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display assistant's response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.llm_app.chat(
                        user_message=prompt,
                        system_prompt=system_prompt if system_prompt else None,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    
                except Exception as e:
                    st.error(f"❌ Error generating response: {str(e)}")
                    st.info("💡 Please check your API key and model availability.")

# Footer
st.divider()
st.caption("Built with ❤️ using Streamlit, Groq, and OpenAI")