import logging
from typing import TYPE_CHECKING

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

if TYPE_CHECKING:
    from app.config.settings import Settings
    from app.rag.index_service import IndexService

logger = logging.getLogger(__name__)

_TRANSFORM_SYSTEM = (
    "Ты переформулируешь вопрос пользователя в один самостоятельный поисковый запрос "
    "на русском языке для семантического поиска по базе документов Сбербанка. Учитывай "
    "историю диалога: раскрой местоимения и отсылки на предыдущие темы. Ответь одной "
    "строкой — только текст запроса, без пояснений и кавычек."
)

_CONTEXT_USER = (
    "Фрагменты документов (контекст):\n\n"
    "{context}\n\n"
    "Вопрос пользователя: {question}\n\n"
    "Сформулируй ответ, опираясь на контекст. Если в контексте нет подходящих фактов, "
    "скажи об этом кратко."
)

_RAG_SYSTEM_SUFFIX = (
    "\n\nПри ответе пользователю опирайся на фрагменты из контекста в его сообщении; "
    "не придумывай конкретные факты, которых нет в этом контексте."
)


def _format_context(docs: list[Document]) -> str:
    parts = []
    for index, doc in enumerate(docs, start=1):
        parts.append(f"[{index}] {doc.page_content}")
    return "\n\n".join(parts)


class RagChain:
    def __init__(self, settings: "Settings", index_service: "IndexService") -> None:
        self._index = index_service
        self._retriever_k = settings.retriever_k
        llm_kwargs = {
            "model": settings.llm_model,
            "openai_api_key": settings.openrouter_api_key,
            "openai_api_base": settings.openrouter_base_url,
            "temperature": 0,
            "request_timeout": settings.llm_timeout_sec,
        }
        self._transform_llm = ChatOpenAI(**llm_kwargs)
        self._llm = ChatOpenAI(**llm_kwargs)

    def is_ready(self) -> bool:
        store = self._index.vector_store
        return store is not None and len(store.store) > 0

    async def answer(
        self,
        question: str,
        history: list[BaseMessage],
        system_prompt: str,
    ) -> str:
        store = self._index.vector_store
        if store is None or len(store.store) == 0:
            raise RuntimeError("vector store is empty")

        transform_messages: list[BaseMessage] = [SystemMessage(content=_TRANSFORM_SYSTEM)]
        transform_messages.extend(history)
        transform_messages.append(
            HumanMessage(content=f"Текущий вопрос: {question}\n\nПоисковый запрос:")
        )
        transform_out = await self._transform_llm.ainvoke(transform_messages)
        search_query = (str(transform_out.content) if transform_out.content else "").strip()
        if not search_query:
            search_query = question
        logger.info("RAG search query length=%s", len(search_query))

        retriever = store.as_retriever(search_kwargs={"k": self._retriever_k})
        docs = await retriever.ainvoke(search_query)
        context = _format_context(list(docs))
        logger.info("RAG retrieved chunks=%s context_length=%s", len(docs), len(context))

        system = system_prompt.strip() + _RAG_SYSTEM_SUFFIX
        gen_messages: list[BaseMessage] = [SystemMessage(content=system)]
        gen_messages.extend(history)
        gen_messages.append(
            HumanMessage(content=_CONTEXT_USER.format(context=context, question=question))
        )
        final = await self._llm.ainvoke(gen_messages)
        answer = (str(final.content) if final.content else "").strip()
        if not answer:
            raise ValueError("LLM returned empty RAG answer")
        logger.info("RAG answer length=%s", len(answer))
        return answer
