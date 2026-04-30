import json
from types import SimpleNamespace

import pytest
from langchain_core.embeddings.fake import FakeEmbeddings

import src.index_service as index_service_module
from src.corpus_loader import CORPUS_JSON_NAME
from src.index_service import IndexService


@pytest.mark.asyncio
async def test_index_service_rebuild_counts_chunks(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(index_service_module, "project_root", lambda: tmp_path)
    corp = tmp_path / "corpus"
    corp.mkdir()
    payload = [
        {"url": "https://x.test", "full_text": "Альфа бета гамма дельта эпсилон " * 80},
    ]
    (corp / CORPUS_JSON_NAME).write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )

    settings = SimpleNamespace(data_dir="corpus", chunk_size=200, chunk_overlap=20)
    emb = FakeEmbeddings(size=128)
    svc = IndexService(settings, emb)  # type: ignore[arg-type]
    n = await svc.rebuild()
    assert n > 0
    assert svc.chunk_count() == n
