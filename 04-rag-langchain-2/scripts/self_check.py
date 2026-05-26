#!/usr/bin/env python3
"""Self-check scripts for local smoke tests."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_core.messages import AIMessage, HumanMessage

from app.config.settings import Settings
from app.services.chat_history import ChatHistory
from app.services.dialog_service import DialogService


def check_chat_history_trim() -> None:
    history = ChatHistory(max_pairs=2)
    chat_id = 1
    for index in range(5):
        if index % 2 == 0:
            history.add_user(chat_id, f"msg-{index}")
        else:
            history.add_assistant(chat_id, f"msg-{index}")

    messages = history.get_messages(chat_id)
    assert len(messages) == 4, f"expected 4 messages, got {len(messages)}"
    assert isinstance(messages[0], AIMessage)
    assert messages[0].content == "msg-1"
    assert isinstance(messages[-1], HumanMessage)
    assert messages[-1].content == "msg-4"
    print("OK: ChatHistory trim keeps last N pairs (LangChain messages)")


async def check_dialog_service_rag() -> None:
    settings = Settings(
        telegram_bot_token="test-token",
        openrouter_api_key="test-key",
        llm_model="test-model",
        embedding_model="openai/text-embedding-3-small",
        retriever_k=4,
        system_prompt="You are a test assistant.",
        history_max_pairs=10,
    )
    chat_history = ChatHistory(max_pairs=settings.history_max_pairs)
    rag_chain = MagicMock()
    rag_chain.is_ready.return_value = True
    rag_chain.answer = AsyncMock(return_value="Test RAG reply")
    dialog = DialogService(settings, chat_history, rag_chain)

    reply = await dialog.reply(42, "Hello")
    assert reply == "Test RAG reply"
    rag_chain.answer.assert_awaited_once()
    question, history, system_prompt = rag_chain.answer.await_args.args
    assert question == "Hello"
    assert history == []
    assert system_prompt == settings.system_prompt
    stored = chat_history.get_messages(42)
    assert len(stored) == 2
    assert isinstance(stored[0], HumanMessage)
    assert stored[0].content == "Hello"
    assert isinstance(stored[1], AIMessage)
    assert stored[1].content == "Test RAG reply"
    print("OK: DialogService → RagChain")


def main() -> int:
    checks = [check_chat_history_trim]

    try:
        asyncio.run(check_dialog_service_rag())
    except Exception as exc:
        print(f"FAIL: dialog service RAG — {exc}", file=sys.stderr)
        return 1

    for check in checks:
        try:
            check()
        except Exception as exc:
            print(f"FAIL: {check.__name__} — {exc}", file=sys.stderr)
            return 1

    print("All self-checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
