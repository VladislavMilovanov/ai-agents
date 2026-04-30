from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings.fake import FakeEmbeddings
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.vectorstores import InMemoryVectorStore

from src.rag_chain import RagChain


class DummyIndex:
    def __init__(self, store: InMemoryVectorStore) -> None:
        self.vector_store = store


@pytest.mark.asyncio
async def test_rag_chain_answer_calls_llm_twice_and_returns_final() -> None:
    emb = FakeEmbeddings(size=384)
    store = InMemoryVectorStore.from_documents(
        [Document(page_content="Якорь: заказ карты через СберБанк Онлайн")],
        embedding=emb,
    )
    idx = DummyIndex(store)
    settings = SimpleNamespace(
        llm_model="test/model",
        openrouter_api_key="x",
        openrouter_base_url="https://openrouter.ai/api/v1",
        retriever_k=2,
    )
    transform_mock = MagicMock()
    transform_mock.ainvoke = AsyncMock(
        return_value=AIMessage(content="как заказать дебетовую карту сбер")
    )
    main_mock = MagicMock()
    main_mock.ainvoke = AsyncMock(
        return_value=AIMessage(content="Опираясь на документ: заказ через СберБанк Онлайн.")
    )
    with patch("src.rag_chain.ChatOpenAI", side_effect=[transform_mock, main_mock]):
        chain = RagChain(settings, idx)  # type: ignore[arg-type]
        out = await chain.answer(
            "А конкретно где оформить?",
            [HumanMessage(content="Хочу карту")],
            "Ты консультант.",
        )
    transform_mock.ainvoke.assert_awaited_once()
    main_mock.ainvoke.assert_awaited_once()
    assert "СберБанк" in out


def test_rag_chain_not_ready_when_empty() -> None:
    emb = FakeEmbeddings(size=384)
    empty = InMemoryVectorStore(embedding=emb)
    idx = DummyIndex(empty)
    settings = SimpleNamespace(
        llm_model="m",
        openrouter_api_key="k",
        openrouter_base_url="https://openrouter.ai/api/v1",
        retriever_k=4,
    )
    with patch("src.rag_chain.ChatOpenAI", side_effect=[MagicMock(), MagicMock()]):
        chain = RagChain(settings, idx)  # type: ignore[arg-type]
    assert chain.is_ready() is False
