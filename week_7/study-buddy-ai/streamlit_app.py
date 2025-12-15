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

with st.sidebar:
    st.header("LLM Settings")

    provider = st.selectbox(
        "Provider",
        options=CATALOG.providers,
        index=CATALOG.providers.index(cfg.default_provider) if cfg.default_provider in CATALOG.providers else 0,
    )

    model_options = CATALOG.models_by_provider.get(provider, [])
    default_model = cfg.default_model if cfg.default_model in model_options else (model_options[0] if model_options else "")
    model = st.selectbox(
        "Model",
        options=model_options,
        index=model_options.index(default_model) if default_model in model_options else 0,
    )

    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=float(cfg.default_temperature), step=0.05)
    max_tokens = st.number_input("Max tokens", min_value=256, max_value=8192, value=int(cfg.default_max_tokens), step=128)

    st.divider()
    st.header("Persona")
    persona_name = st.selectbox("Persona", options=list(PERSONAS.keys()), index=0)
    persona_prompt = PERSONAS[persona_name].system_prompt

    st.caption("Keys are read from environment variables. Use GROQ_API_KEY or OPENAI_API_KEY.")


tab_chat, tab_quiz = st.tabs(["Chat", "Quiz Generator"])


def get_llm_cached():
    cache_key = f"{provider}:{model}:{temperature}:{max_tokens}"
    if (
        "llm_cache_key" not in st.session_state
        or st.session_state.llm_cache_key != cache_key
        or "llm_instance" not in st.session_state
    ):
        st.session_state.llm_cache_key = cache_key
        st.session_state.llm_instance = build_llm(
            cfg=cfg,
            provider=provider,
            model=model,
            temperature=float(temperature),
            max_tokens=int(max_tokens),
        )
    return st.session_state.llm_instance


with tab_chat:
    st.subheader("Chat with your Study Buddy")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_text = st.chat_input("Ask something, for example. Explain Spark shuffle and quiz me.")
    if user_text:
        st.session_state.chat_history.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

        try:
            llm = get_llm_cached()
            answer = chat_reply(llm=llm, persona_prompt=persona_prompt, history=st.session_state.chat_history)
        except Exception as e:
            answer = f"Error. {e}"

        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)


with tab_quiz:
    st.subheader("Generate a Quiz")

    topic = st.text_area(
        "Topic or context",
        placeholder="Paste notes or write a topic, for example. Kafka consumer groups and offsets.",
    )

    col1, col2 = st.columns(2)
    with col1:
        quiz_kind = st.selectbox("Quiz type", options=["multiple_choice", "open_ended"], index=0)
    with col2:
        num_questions = st.number_input("Number of questions", min_value=1, max_value=20, value=5, step=1)

    if st.button("Generate quiz", type="primary", disabled=not bool(topic.strip())):
        try:
            llm = get_llm_cached()
            quiz = generate_quiz(
                llm=llm,
                topic=topic.strip(),
                num_questions=int(num_questions),
                quiz_type=quiz_kind,
            )
            st.session_state.generated_quiz = quiz
        except Exception as e:
            st.error(f"Quiz generation failed. {e}")
            st.stop()

    quiz = st.session_state.get("generated_quiz")
    if quiz:
        st.success("Quiz generated.")

        if quiz_kind == "multiple_choice":
            for i, q in enumerate(quiz.questions, start=1):
                st.markdown(f"### Q{i}. {q.question}")
                choice = st.radio(
                    label="Select an answer",
                    options=q.options,
                    key=f"mcq_{i}",
                    index=None,
                )
                if st.button(f"Check Q{i}", key=f"check_mcq_{i}"):
                    if choice is None:
                        st.warning("Pick an option first.")
                    elif choice.strip().lower() == q.answer.strip().lower():
                        st.success("Correct.")
                    else:
                        st.error(f"Incorrect. Correct answer. {q.answer}")

        else:
            for i, q in enumerate(quiz.questions, start=1):
                st.markdown(f"### Q{i}. {q.question}")
                user_ans = st.text_input("Your answer", key=f"oe_{i}")
                if st.button(f"Check Q{i}", key=f"check_oe_{i}"):
                    if not user_ans.strip():
                        st.warning("Type an answer first.")
                    else:
                        st.info(f"Reference answer. {q.answer}")
