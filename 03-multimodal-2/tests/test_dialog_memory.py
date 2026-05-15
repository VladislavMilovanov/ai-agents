import unittest
from typing import cast

from tg_llm_bot.dialog_service import DialogService
from tg_llm_bot.llm_client import LlmClient


class _FakeLlm:
    def __init__(self) -> None:
        self.last_messages: list[dict[str, str]] | None = None

    async def complete(self, messages: list[dict[str, str]]) -> str:
        self.last_messages = list(messages)
        return "ok"


class DialogMemoryTests(unittest.IsolatedAsyncioTestCase):
    async def test_second_turn_includes_first_user_message(self) -> None:
        fake = _FakeLlm()
        dialog = DialogService(
            system_prompt="SYS",
            llm=cast(LlmClient, fake),
            max_messages=20,
        )
        await dialog.reply(1, "первое")
        await dialog.reply(1, "второе")
        assert fake.last_messages is not None
        user_contents = [m["content"] for m in fake.last_messages if m["role"] == "user"]
        self.assertIn("первое", user_contents)
        self.assertIn("второе", user_contents)

    async def test_sliding_window_respects_env_limit(self) -> None:
        fake = _FakeLlm()
        dialog = DialogService(
            system_prompt="SYS",
            llm=cast(LlmClient, fake),
            max_messages=4,
        )
        for i in range(3):
            await dialog.reply(42, f"msg-{i}")
        assert fake.last_messages is not None
        users = [m["content"] for m in fake.last_messages if m["role"] == "user"]
        self.assertNotIn("msg-0", users)
        self.assertIn("msg-1", users)
        self.assertIn("msg-2", users)


if __name__ == "__main__":
    unittest.main()
