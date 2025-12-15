from typing import Dict, List

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def to_lc_messages(persona_prompt: str, history: List[Dict[str, str]]):
    messages = [SystemMessage(content=persona_prompt)]
    for item in history:
        role = item.get("role", "").strip().lower()
        content = item.get("content", "")

        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages


def chat_reply(llm, persona_prompt: str, history: List[Dict[str, str]]) -> str:
    messages = to_lc_messages(persona_prompt, history)
    result = llm.invoke(messages)
    return getattr(result, "content", str(result))
