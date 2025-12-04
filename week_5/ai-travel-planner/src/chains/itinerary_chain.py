from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.config.config import GROQ_API_KEY
from src.utils.logger import get_logger

logger = get_logger(__name__)

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile",
    temperature=0.3
)

itinerary_prompt = ChatPromptTemplate([
    ("system", """You are a helpful travel assistant. Create a detailed day trip itinerary for {city} based on the user's interests: {interests}.

Please provide:
- A structured timeline from morning to evening
- Specific places to visit
- Estimated time at each location
- Tips for each location
- Suggested restaurants/cafes for meals

Format the response with clear sections and bullet points for easy reading."""),
    ("human", "Create an itinerary for my day trip")
])

def generate_itinerary(city: str, interests: list[str]) -> str:
    """Generate a travel itinerary using LLM"""
    try:
        logger.info(f"Generating itinerary for {city} with interests: {interests}")
        
        response = llm.invoke(
            itinerary_prompt.format_messages(city=city, interests=', '.join(interests))
        )
        
        logger.info("Itinerary generated successfully")
        return response.content
    
    except Exception as e:
        logger.error(f"Error generating itinerary: {e}")
        raise
