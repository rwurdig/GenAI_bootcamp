import streamlit as st

from src.chat.engine import chat_reply
from src.chat.personas import PERSONAS
from src.config import load_config
from src.llm.factory import build_llm
from src.llm.models import CATALOG
from src.quiz.generator import generate_quiz

st.set_page_config(page_title="Study Buddy AI", layout="wide")

cfg = load_config()

st.title("Study Buddy AI")

# sidebar - llm settings
with st.sidebar:
    st.header("LLM Settings")

    provider = st.selectbox(
        "Provider",
        CATALOG.providers,
        index=CATALOG.providers.index(cfg.default_provider) if cfg.default_provider in CATALOG.providers else 0,
    )

    models = CATALOG.models_by_provider.get(provider, [])
    default_model = cfg.default_model if cfg.default_model in models else (models[0] if models else "")
    model = st.selectbox(
        "Model",
        models,
        index=models.index(default_model) if default_model in models else 0,
    )

    temperature = st.slider("Temperature", 0.0, 1.0, float(cfg.default_temperature), 0.05)
    max_tokens = st.number_input("Max tokens", 256, 8192, int(cfg.default_max_tokens), 128)

    st.divider()
    st.header("Persona")
    persona_name = st.selectbox("Persona", list(PERSONAS.keys()))

    st.caption("Set GROQ_API_KEY or OPENAI_API_KEY env var")


def get_llm():
    """Cache LLM instance until settings change"""
    key = f"{provider}:{model}:{temperature}:{max_tokens}"

    if st.session_state.get("_llm_key") != key:
        st.session_state._llm_key = key
        st.session_state._llm = build_llm(cfg, provider, model, temperature, max_tokens)

    return st.session_state._llm


tab_chat, tab_quiz = st.tabs(["Chat", "Quiz Generator"])


# ---- Chat tab ----
with tab_chat:
    st.subheader("Chat with your Study Buddy")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask something...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            llm = get_llm()
            answer = chat_reply(llm, PERSONAS[persona_name].system_prompt, st.session_state.chat_history)
        except Exception as e:
            answer = f"Error: {e}"

        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)


# ---- Quiz tab ----
with tab_quiz:
    st.subheader("Generate a Quiz")

    topic = st.text_area("Topic or context", placeholder="Paste notes or describe a topic...")

    col1, col2 = st.columns(2)
    with col1:
        quiz_type = st.selectbox("Type", ["multiple_choice", "open_ended"])
    with col2:
        num_q = st.number_input("Questions", 1, 20, 5)

    if st.button("Generate", type="primary", disabled=not topic.strip()):
        try:
            llm = get_llm()
            quiz = generate_quiz(llm, topic.strip(), int(num_q), quiz_type)
            st.session_state.quiz = quiz
            st.session_state.quiz_type = quiz_type
        except Exception as e:
            st.error(f"Failed: {e}")
            st.stop()

    # display quiz if exists
    if "quiz" in st.session_state:
        quiz = st.session_state.quiz
        st.success("Quiz ready!")

        for i, q in enumerate(quiz.questions, 1):
            st.markdown(f"**Q{i}.** {q.question}")

            if st.session_state.quiz_type == "multiple_choice":
                choice = st.radio("Answer:", q.options, key=f"q{i}", index=None)
                if st.button(f"Check Q{i}", key=f"chk{i}"):
                    if not choice:
                        st.warning("Pick an option")
                    elif choice.lower().strip() == q.answer.lower().strip():
                        st.success("Correct!")
                    else:
                        st.error(f"Wrong. Answer: {q.answer}")
            else:
                ans = st.text_input("Your answer:", key=f"q{i}")
                if st.button(f"Check Q{i}", key=f"chk{i}"):
                    if not ans.strip():
                        st.warning("Enter an answer")
                    else:
                        st.info(f"Reference: {q.answer}")
