from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


def chat_reply(llm, persona_prompt: str, history: list) -> str:
    """Send chat history to LLM with persona system prompt"""

    messages = [SystemMessage(content=persona_prompt)]

    for msg in history:
        role = msg.get("role", "").lower()
        content = msg.get("content", "")

        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    result = llm.invoke(messages)
    return getattr(result, "content", str(result))
