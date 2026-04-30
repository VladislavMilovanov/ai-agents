from types import SimpleNamespace

from src.llm_client import _is_ollama_openai_base, _message_text_for_json


def test_is_ollama_detects_local_port() -> None:
    assert _is_ollama_openai_base("http://127.0.0.1:11434/v1")
    assert _is_ollama_openai_base("http://192.168.1.2:11434/v1/")
    assert not _is_ollama_openai_base("https://openrouter.ai/api/v1")


def test_message_text_prefers_content() -> None:
    msg = SimpleNamespace(content='{"action":"unknown"}', reasoning="")
    assert _message_text_for_json(msg) == '{"action":"unknown"}'


def test_message_text_finds_json_in_reasoning() -> None:
    reasoning = (
        "Думаю...\n"
        '{"action": "transaction", "transaction": {"occurred_at": '
        '"2026-05-01T12:00:00", "direction": "expense", "amount": 100, '
        '"expense_type": "daily", "category": "продукты", '
        '"description": "хлеб"}}\nконец'
    )
    msg = SimpleNamespace(content="", reasoning=reasoning)
    out = _message_text_for_json(msg)
    assert '"action"' in out
    assert "transaction" in out
