import json
import re
from typing import Literal, Union

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.quiz.prompts import MULTIPLE_CHOICE_PROMPT, OPEN_ENDED_PROMPT
from src.quiz.schemas import MultipleChoiceQuiz, OpenEndedQuiz


QuizType = Literal["multiple_choice", "open_ended"]
QuizSchema = Union[MultipleChoiceQuiz, OpenEndedQuiz]


def _extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in model output.")
    return match.group(0)


def generate_quiz(llm, topic: str, num_questions: int, quiz_type: QuizType) -> QuizSchema:
    if quiz_type == "multiple_choice":
        schema_model = MultipleChoiceQuiz
        template = MULTIPLE_CHOICE_PROMPT
    else:
        schema_model = OpenEndedQuiz
        template = OPEN_ENDED_PROMPT

    parser = PydanticOutputParser(pydantic_object=schema_model)
    schema_instructions = parser.get_format_instructions()

    prompt = ChatPromptTemplate.from_template(template).format_prompt(
        topic=topic,
        num_questions=num_questions,
        schema=schema_instructions,
    )

    raw = llm.invoke(prompt.to_messages())
    content = getattr(raw, "content", str(raw))

    try:
        return parser.parse(content)
    except Exception:
        cleaned = _extract_json(content)
        obj = json.loads(cleaned)
        return schema_model.model_validate(obj)
