from langchain_core.messages import AIMessage, HumanMessage

from src.llm_client import base_messages_to_openai


def test_base_messages_to_openai_maps_roles() -> None:
    history = [
        HumanMessage(content="u1"),
        AIMessage(content="a1"),
    ]
    rows = base_messages_to_openai(history)
    assert rows == [
        {"role": "user", "content": "u1"},
        {"role": "assistant", "content": "a1"},
    ]
