from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.utils.llm import get_llm

RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You answer strictly from the context. If the answer is not present, say 'I don't know'. Cite sources."),
    ("human", "Question: {question}\n\nContext:\n{context}")
])

def ask(vect, question: str, provider: str = "auto", model: str = None, temperature: float = 0.1, k: int = 4) -> str:
    retr = vect.as_retriever(search_kwargs={"k": k})
    docs = retr.invoke(question)
    context_parts = []
    for doc in docs:
        source = doc.metadata.get("source", "?") if hasattr(doc, "metadata") else "?"
        content = doc.page_content if hasattr(doc, "page_content") else str(doc)
        context_parts.append(f"[Source: {source}]\n{content}")
    context = "\n\n".join(context_parts)
    llm = get_llm(provider=provider, model=model, temperature=temperature)
    chain = RAG_PROMPT | llm | StrOutputParser()
    return chain.invoke({"question": question, "context": context})