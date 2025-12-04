from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

from app.components.llm import load_llm
from app.components.vector_store import load_vector_store

from app.common.logger import get_logger
from app.common.custom_exception import CustomException

logger = get_logger(__name__)

CUSTOM_PROMPT_TEMPLATE = """You are a knowledgeable and helpful medical assistant. Your goal is to provide clear, accurate, and actionable health information.

INSTRUCTIONS:
1. Answer the question directly and thoroughly using the provided context
2. Use bullet points and numbered lists for clarity when listing treatments or steps
3. If the question is about recovery or treatment, provide specific actionable steps
4. Always include relevant warnings or when to seek emergency care
5. End with a reminder to consult a healthcare professional for personalized advice

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

def set_custom_prompt():
    return PromptTemplate(template=CUSTOM_PROMPT_TEMPLATE, input_variables=["context", "question"])

def create_qa_chain():
    try:
        logger.info("Loading vector store for context")
        db = load_vector_store()

        if db is None:
            raise CustomException("Vector store not present or empty")

        llm = load_llm()

        if llm is None:
            raise CustomException("LLM not loaded")

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=db.as_retriever(search_kwargs={'k': 3}),
            return_source_documents=False,
            chain_type_kwargs={'prompt': set_custom_prompt()}
        )

        logger.info("Successfully created the QA chain")
        return qa_chain

    except Exception as e:
        error_message = CustomException("Failed to make a QA chain", e)
        logger.error(str(error_message))
        return None
