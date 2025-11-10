from typing import Literal, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from src.utils.text import chunk_text
from src.utils.llm import get_llm

SummaryType = Literal["concise", "detailed", "bullets"]

NEWS_MAP_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful analyst. Summarize the following section in 2-4 bullet points. Keep facts only."),
    ("human", "{chunk}")
])

NEWS_REDUCE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful analyst. Combine the points into a final {style} summary. Include a one-line TL;DR and 5-7 key bullets."),
    ("human", "Points from all sections:\n\n{points}\n\nReturn a clean markdown summary.")
])

def summarize_article_text(text: str, provider: str = "auto", model: str = None, style: SummaryType = "detailed", temperature: float = 0.1) -> Dict[str, Any]:
    llm = get_llm(provider=provider, model=model, temperature=temperature)
    chunks = chunk_text(text, chunk_size=1200, chunk_overlap=150)

    # Map step
    map_chain = NEWS_MAP_PROMPT | llm | StrOutputParser()
    points = []
    for c in chunks:
        points.append(map_chain.invoke({"chunk": c}))

    reduce_chain = NEWS_REDUCE_PROMPT | llm | StrOutputParser()
    final = reduce_chain.invoke({"points": "\n".join(points), "style": style})
    return {"chunks": len(chunks), "points": points, "summary": final}