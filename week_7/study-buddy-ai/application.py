import os
import tempfile
from dataclasses import dataclass

import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    llm_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))


def get_llm() -> ChatGroq:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY. Add it to .env")

    return ChatGroq(
        groq_api_key=api_key,
        model_name=AppConfig().llm_model,
        temperature=0.2,
        max_tokens=512,
    )


@st.cache_resource(show_spinner=False)
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=AppConfig().embedding_model)


def split_documents(documents: list[Document]) -> list[Document]:
    cfg = AppConfig()
    splitter = RecursiveCharacterTextSplitter(chunk_size=cfg.chunk_size, chunk_overlap=cfg.chunk_overlap)
    return splitter.split_documents(documents)


def docs_from_text(text: str, source: str) -> list[Document]:
    return [Document(page_content=text, metadata={"source": source})]


def docs_from_uploaded_files(files) -> list[Document]:
    documents: list[Document] = []

    # Lazy import so app still starts without PDF deps when not used
    from langchain_community.document_loaders import PyPDFLoader

    for uploaded in files:
        suffix = os.path.splitext(uploaded.name)[1].lower()

        if suffix not in {".pdf", ".txt"}:
            st.warning(f"Skipping unsupported file: {uploaded.name}")
            continue

        if suffix == ".txt":
            text = uploaded.read().decode("utf-8", errors="ignore")
            documents.extend(docs_from_text(text, uploaded.name))
            continue

        # PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        try:
            loader = PyPDFLoader(tmp_path)
            pdf_docs = loader.load()
            for d in pdf_docs:
                d.metadata = {**(d.metadata or {}), "source": uploaded.name}
            documents.extend(pdf_docs)
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    return documents


def build_vectorstore(documents: list[Document]) -> FAISS:
    chunks = split_documents(documents)
    if not chunks:
        raise RuntimeError("No content to index. Add notes or upload files.")

    return FAISS.from_documents(chunks, get_embeddings())


def make_answer(llm: ChatGroq, context: str, question: str) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are Study Buddy AI. Use the provided context to answer clearly and helpfully.

Rules:
- Prefer structured output (bullets/steps) when helpful.
- If the context does not contain the answer, say what is missing and suggest what to upload/add.
- Keep the tone friendly and concise.

CONTEXT:\n{context}""",
            ),
            ("human", "Question: {question}"),
        ]
    )

    chain = prompt | llm
    result = chain.invoke({"context": context, "question": question})
    return (getattr(result, "content", None) or str(result)).strip()


def retrieve_context(vs: FAISS, question: str) -> str:
    docs = vs.similarity_search(question, k=4)
    parts = []
    for i, d in enumerate(docs, start=1):
        src = (d.metadata or {}).get("source", "unknown")
        parts.append(f"[Source {i}: {src}]\n{d.page_content}")
    return "\n\n".join(parts)


def main() -> None:
    st.set_page_config(page_title="Study Buddy AI", page_icon="📚")

    st.title("📚 Study Buddy AI")
    st.caption("Upload notes/PDFs or paste text, then ask questions.")

    with st.sidebar:
        st.header("Setup")
        st.write("Add your Groq key in `.env`.")
        st.code("GROQ_API_KEY=...", language="bash")

        mode = st.radio("Knowledge Source", ["Paste notes", "Upload files"], index=0)

        if mode == "Upload files":
            uploads = st.file_uploader("Upload PDF/TXT", accept_multiple_files=True, type=["pdf", "txt"])
            pasted = ""
        else:
            uploads = []
            pasted = st.text_area("Paste notes or textbook excerpts", height=200)

        build_clicked = st.button("Build / Rebuild Index", type="primary")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None

    if build_clicked:
        try:
            if mode == "Upload files":
                docs = docs_from_uploaded_files(uploads)
            else:
                docs = docs_from_text(pasted.strip(), "pasted_notes") if pasted.strip() else []

            st.session_state.vectorstore = build_vectorstore(docs)
            st.success("Index ready. Ask your questions below.")
        except Exception as e:
            st.session_state.vectorstore = None
            st.error(str(e))

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Ask a question about your materials")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            if st.session_state.vectorstore is None:
                st.warning("No index yet. Click **Build / Rebuild Index** in the sidebar first.")
                return

            try:
                llm = get_llm()
                context = retrieve_context(st.session_state.vectorstore, question)
                answer = make_answer(llm, context, question)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(str(e))


if __name__ == "__main__":
    main()
