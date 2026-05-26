from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document
from langchain_core.embeddings.fake import FakeEmbeddings
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.vectorstores import InMemoryVectorStore

from app.rag.rag_chain import RagChain


class DummyIndex:
    def __init__(self, store: InMemoryVectorStore) -> None:
        self.vector_store = store


@pytest.mark.asyncio
async def test_rag_chain_answer_calls_llm_twice_and_returns_final() -> None:
    embeddings = FakeEmbeddings(size=384)
    store = InMemoryVectorStore.from_documents(
        [Document(page_content="Заказ карты через СберБанк Онлайн")],
        embedding=embeddings,
    )
    index = DummyIndex(store)
    settings = SimpleNamespace(
        llm_model="test/model",
        openrouter_api_key="x",
        openrouter_base_url="https://openrouter.ai/api/v1",
        retriever_k=2,
        llm_timeout_sec=60,
    )
    transform_mock = MagicMock()
    transform_mock.ainvoke = AsyncMock(
        return_value=AIMessage(content="как заказать дебетовую карту сбер"),
    )
    main_mock = MagicMock()
    main_mock.ainvoke = AsyncMock(
        return_value=AIMessage(content="Опираясь на документ: заказ через СберБанк Онлайн."),
    )
    with patch("app.rag.rag_chain.ChatOpenAI", side_effect=[transform_mock, main_mock]):
        chain = RagChain(settings, index)  # type: ignore[arg-type]
        answer = await chain.answer(
            "А где оформить?",
            [HumanMessage(content="Хочу карту")],
            "Ты консультант Сбера.",
        )
    transform_mock.ainvoke.assert_awaited_once()
    main_mock.ainvoke.assert_awaited_once()
    assert "СберБанк" in answer


def test_rag_chain_not_ready_when_empty() -> None:
    embeddings = FakeEmbeddings(size=384)
    empty_store = InMemoryVectorStore(embedding=embeddings)
    index = DummyIndex(empty_store)
    settings = SimpleNamespace(
        llm_model="m",
        openrouter_api_key="k",
        openrouter_base_url="https://openrouter.ai/api/v1",
        retriever_k=4,
        llm_timeout_sec=60,
    )
    with patch("app.rag.rag_chain.ChatOpenAI", side_effect=[MagicMock(), MagicMock()]):
        chain = RagChain(settings, index)  # type: ignore[arg-type]
    assert chain.is_ready() is False
