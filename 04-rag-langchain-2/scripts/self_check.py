#!/usr/bin/env python3
"""Self-check scripts for MVP iterations."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config.settings import Settings
from app.llm.openrouter_client import OpenRouterClient
from app.models.chat_message import ChatMessage
from app.rag.context_provider import ContextProvider
from app.services.chat_history import ChatHistory
from app.services.dialog_service import DialogService


def check_chat_history_trim() -> None:
    history = ChatHistory(max_pairs=2)
    chat_id = 1
    for index in range(5):
        role = "user" if index % 2 == 0 else "assistant"
        history.add(chat_id, ChatMessage(role=role, content=f"msg-{index}"))

    messages = history.get_messages(chat_id)
    assert len(messages) == 4, f"expected 4 messages, got {len(messages)}"
    assert messages[0].content == "msg-1"
    assert messages[-1].content == "msg-4"
    print("OK: ChatHistory trim keeps last N pairs")


async def check_dialog_service_layers() -> None:
    settings = Settings(
        telegram_bot_token="test-token",
        openrouter_api_key="test-key",
        llm_model="test-model",
        system_prompt="You are a test assistant.",
        history_max_pairs=10,
    )
    chat_history = ChatHistory(max_pairs=settings.history_max_pairs)
    client = OpenRouterClient(settings)
    dialog = DialogService(settings, chat_history, client, ContextProvider())

    with patch.object(client, "complete", new_callable=AsyncMock) as mock_complete:
        mock_complete.return_value = "Test reply"
        reply = await dialog.reply(42, "Hello")

    assert reply == "Test reply"
    mock_complete.assert_awaited_once()
    sent_messages = mock_complete.await_args.args[0]
    assert sent_messages[0]["role"] == "system"
    assert sent_messages[0]["content"] == settings.system_prompt
    assert sent_messages[-1]["role"] == "user"
    assert sent_messages[-1]["content"] == "Hello"
    stored = chat_history.get_messages(42)
    assert len(stored) == 2
    assert stored[0].role == "user"
    assert stored[1].role == "assistant"
    print("OK: DialogService → ContextProvider → OpenRouterClient chain")


async def check_llm_integration() -> None:
    settings = Settings()
    client = OpenRouterClient(settings)
    answer = await client.complete(
        [
            {"role": "system", "content": settings.system_prompt},
            {"role": "user", "content": "Ответь одним словом: да"},
        ]
    )
    assert answer.strip(), "empty LLM response"
    print(f"OK: OpenRouter integration (response length={len(answer)})")


def main() -> int:
    checks = [check_chat_history_trim]

    try:
        asyncio.run(check_dialog_service_layers())
    except Exception as exc:
        print(f"FAIL: dialog service layers — {exc}", file=sys.stderr)
        return 1

    try:
        asyncio.run(check_llm_integration())
    except Exception as exc:
        print(f"FAIL: LLM integration — {exc}", file=sys.stderr)
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
