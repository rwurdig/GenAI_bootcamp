from typing import Dict, Any, Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from src.utils.text import chunk_text
from src.utils.llm import get_llm, get_embeddings
from src.utils.youtube import get_youtube_transcript, download_audio_with_ytdlp
from src.utils.audio import transcribe_audio

SUMMARY_MAP_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Summarize the following transcript section in 2-3 concise bullets (facts only)."),
    ("human", "{chunk}")
])

SUMMARY_REDUCE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "Combine all points into a readable summary with TL;DR and 5-7 bullets. Keep neutral tone."),
    ("human", "{points}")
])

QA_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Answer strictly using the provided context. If unsure, say you don't know."),
    ("human", "Question: {question}\n\nContext:\n{context}")
])

def process_youtube(url: str, provider: str = "auto", model: str = None, embeddings_provider: str = None, temperature: float = 0.1, persist_dir: str = None) -> Dict[str, Any]:
    # 1) Transcript or STT
    transcript = get_youtube_transcript(url)
    if not transcript:
        print(f"No transcript available for {url}, attempting audio download...")
        audio_path = download_audio_with_ytdlp(url)
        if not audio_path:
            raise RuntimeError(
                "Could not get transcript or download audio. "
                "This may be due to: (1) Invalid YouTube URL, (2) Video has no captions and download failed, "
                "(3) Network connectivity issues, or (4) Age-restricted/private video."
            )
        print(f"Audio downloaded to {audio_path}, transcribing...")
        try:
            transcript = transcribe_audio(audio_path)
            print(f"Transcription completed: {len(transcript)} characters")
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")

    # 2) Summarize (map-reduce)
    try:
        print(f"Getting LLM with provider={provider}, model={model}")
        llm = get_llm(provider=provider, model=model, temperature=temperature)
        print("LLM initialized successfully")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize LLM: {e}")
    
    try:
        chunks = chunk_text(transcript, chunk_size=1200, chunk_overlap=150)
        print(f"Text chunked into {len(chunks)} pieces")
    except Exception as e:
        raise RuntimeError(f"Failed to chunk text: {e}")

    try:
        map_chain = SUMMARY_MAP_PROMPT | llm | StrOutputParser()
        partial = [map_chain.invoke({"chunk": c}) for c in chunks]
        print(f"Map phase completed: {len(partial)} summaries")
    except Exception as e:
        raise RuntimeError(f"Failed in map phase: {e}")
    
    try:
        reduce_chain = SUMMARY_REDUCE_PROMPT | llm | StrOutputParser()
        summary = reduce_chain.invoke({"points": "\n".join(partial)})
        print("Reduce phase completed")
    except Exception as e:
        raise RuntimeError(f"Failed in reduce phase: {e}")

    # 3) Vectorize
    try:
        print(f"Getting embeddings with provider={embeddings_provider}")
        emb = get_embeddings(embeddings_provider)
        print("Embeddings initialized successfully")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize embeddings: {e}")
    
    try:
        docs = [Document(page_content=c) for c in chunks]
        print(f"Created {len(docs)} documents")
    except Exception as e:
        raise RuntimeError(f"Failed to create documents: {e}")
    
    try:
        print(f"Creating vector store in {persist_dir or '.chroma/video'}")
        vect = Chroma.from_documents(docs, embedding=emb, persist_directory=persist_dir or ".chroma/video")
        vect.persist()
        print("Vector store created successfully")
    except Exception as e:
        raise RuntimeError(f"Failed to create vector store: {e}")

    return {
        "transcript_chars": len(transcript),
        "chunks": len(chunks),
        "summary": summary,
        "vector": vect,
    }

def qa_over_documents(vect, question: str, provider: str = "auto", model: str = None, temperature: float = 0.1, k: int = 4) -> str:
    llm = get_llm(provider=provider, model=model, temperature=temperature)
    retr = vect.as_retriever(search_kwargs={"k": k})
    docs = retr.invoke(question)
    context_sections = []
    for doc in docs:
        source = doc.metadata.get("source", "?") if hasattr(doc, "metadata") else "?"
        content = doc.page_content if hasattr(doc, "page_content") else str(doc)
        context_sections.append(f"[Source: {source}]\n{content}")
    context = "\n\n".join(context_sections)
    chain = QA_PROMPT | llm | StrOutputParser()
    return chain.invoke({"question": question, "context": context})