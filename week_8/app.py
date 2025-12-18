import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Must be first Streamlit command
st.set_page_config(
    page_title="SuperTech Store Support",
    page_icon="🖥️",
    layout="centered",
)


# Load local .env for development (Hugging Face Space secrets are injected as env vars)
load_dotenv()


@st.cache_resource
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found. Please add it in Space secrets.")
        return None
    return Groq(api_key=api_key)


client = get_groq_client()


SYSTEM_PROMPT = """You are a helpful customer support agent for SuperTech Store,
a company selling computer products like monitors, printers, keyboards, and accessories.

You can help customers with:
- Product information and availability
- Order status and tracking
- Return and warranty policies
- Troubleshooting common issues

Be friendly, professional, and concise. If you don't know something, say so honestly.

Available MCP tools (mention these exist but simulate responses for now):
- list_products: Get all products
- search_products: Search by keyword
- get_order: Check order status
- get_customer: Get customer info
"""

import streamlit as st

# MUST be the very first Streamlit command - nothing else before this!
st.set_page_config(
    page_title="SuperTech Store Support",
    page_icon="🖥️",
    layout="centered",
)

import os

from groq import Groq


# Initialize Groq client
@st.cache_resource
def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not found. Please add it in Space secrets.")
        return None
    return Groq(api_key=api_key)


client = get_groq_client()


# System prompt
SYSTEM_PROMPT = """You are a helpful customer support agent for SuperTech Store,
a company selling computer products like monitors, printers, keyboards, and accessories.

You can help customers with:
- Product information and availability
- Order status and tracking
- Return and warranty policies
- Troubleshooting common issues

Be friendly, professional, and concise."""


def _build_groq_messages():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
    return messages


def _generate_assistant_reply() -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=_build_groq_messages(),
        max_tokens=500,
        temperature=0.7,
    )
    return response.choices[0].message.content or ""


# UI Header
st.title("🖥️ SuperTech Store Support")
st.markdown("Welcome! I'm here to help with your computer product questions.")


# Quick action buttons
st.markdown("### Quick Actions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📦 Check Order"):
        st.session_state.quick_action = "I want to check my order status"

with col2:
    if st.button("🔍 Products"):
        st.session_state.quick_action = "What products do you have?"

with col3:
    if st.button("↩️ Returns"):
        st.session_state.quick_action = "What is your return policy?"


st.markdown("---")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Consume quick action (if any) as input for this run
user_input = None
if "quick_action" in st.session_state:
    user_input = st.session_state.quick_action
    del st.session_state.quick_action


# Chat input
prompt = st.chat_input("How can I help you today?")
if prompt:
    user_input = prompt


if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        if not client:
            st.error("Unable to connect to LLM. Check API key.")
        else:
            try:
                with st.spinner("Thinking..."):
                    assistant_message = _generate_assistant_reply()
            except Exception as e:
                st.error(f"Groq request failed: {e}")
            else:
                st.markdown(assistant_message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_message}
                )


# Sidebar
with st.sidebar:
    st.markdown("### About")
    st.markdown("Customer support chatbot for SuperTech Store.")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
