import asyncio
import logging
from pathlib import Path

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import Settings
from app.rag.corpus_loader import CORPUS_JSON_NAME, CorpusLoader

logger = logging.getLogger(__name__)


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class IndexService:
    def __init__(self, settings: Settings, embeddings: OpenAIEmbeddings) -> None:
        self._embeddings = embeddings
        self._data_dir = project_root() / settings.data_dir
        self._vector_store: InMemoryVectorStore | None = None
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

    @property
    def vector_store(self) -> InMemoryVectorStore | None:
        return self._vector_store

    def chunk_count(self) -> int:
        if self._vector_store is None:
            return 0
        return len(self._vector_store.store)

    def set_empty_store(self) -> None:
        self._vector_store = InMemoryVectorStore(embedding=self._embeddings)

    def _rebuild_sync(self) -> int:
        loader = CorpusLoader(self._data_dir)
        documents = loader.load_documents()
        if not documents:
            logger.warning("No corpus documents loaded; index is empty")
            self._vector_store = InMemoryVectorStore(embedding=self._embeddings)
            return 0
        json_docs = [doc for doc in documents if doc.metadata.get("source") == CORPUS_JSON_NAME]
        pdf_docs = [doc for doc in documents if doc.metadata.get("source") != CORPUS_JSON_NAME]
        pdf_chunks = self._splitter.split_documents(pdf_docs) if pdf_docs else []
        splits = pdf_chunks + json_docs
        logger.info(
            "Indexing %s chunks from %s source documents (PDF chunks: %s, JSON: %s)",
            len(splits),
            len(documents),
            len(pdf_chunks),
            len(json_docs),
        )
        self._vector_store = InMemoryVectorStore.from_documents(
            documents=splits,
            embedding=self._embeddings,
        )
        return len(self._vector_store.store)

    async def rebuild(self) -> int:
        return await asyncio.to_thread(self._rebuild_sync)
