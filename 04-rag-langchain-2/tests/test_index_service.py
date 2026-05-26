import json
from types import SimpleNamespace

import pytest
from langchain_core.embeddings.fake import FakeEmbeddings

import app.rag.index_service as index_service_module
from app.rag.corpus_loader import CORPUS_JSON_NAME
from app.rag.index_service import IndexService


@pytest.mark.asyncio
async def test_index_service_rebuild_counts_chunks(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(index_service_module, "project_root", lambda: tmp_path)
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    payload = [
        {"url": "https://x.test", "full_text": "Альфа бета гамма дельта эпсилон " * 80},
    ]
    (corpus_dir / CORPUS_JSON_NAME).write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )

    settings = SimpleNamespace(data_dir="corpus", chunk_size=200, chunk_overlap=20)
    embeddings = FakeEmbeddings(size=128)
    service = IndexService(settings, embeddings)  # type: ignore[arg-type]
    chunk_count = await service.rebuild()
    assert chunk_count == 1
    assert service.chunk_count() == chunk_count
