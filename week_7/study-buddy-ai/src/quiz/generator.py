import json
import re

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.quiz.prompts import MCQ_PROMPT, OPEN_PROMPT
from src.quiz.schemas import MCQQuiz, OpenQuiz


def _extract_json(text: str) -> str:
    """Pull JSON object from LLM response that might have extra text"""
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON found in response")
    return match.group(0)


def generate_quiz(llm, topic: str, num_questions: int, quiz_type: str):
    """
    Generate quiz from topic.
    quiz_type: 'multiple_choice' or 'open_ended'
    """

    if quiz_type == "multiple_choice":
        schema = MCQQuiz
        template = MCQ_PROMPT
    else:
        schema = OpenQuiz
        template = OPEN_PROMPT

    parser = PydanticOutputParser(pydantic_object=schema)

    prompt = ChatPromptTemplate.from_template(template).format_prompt(
        topic=topic,
        num_questions=num_questions,
        schema=parser.get_format_instructions(),
    )

    raw = llm.invoke(prompt.to_messages())
    content = getattr(raw, "content", str(raw))

    # try parsing directly, fallback to extracting json
    try:
        return parser.parse(content)
    except Exception:
        cleaned = _extract_json(content)
        return schema.model_validate(json.loads(cleaned))
