import json
from pathlib import Path

from app.rag.corpus_loader import CORPUS_JSON_NAME, CorpusLoader


def test_corpus_loader_loads_json_faq(tmp_path: Path) -> None:
    payload = [
        {
            "url": "https://example.com",
            "full_text": "Категория: Тест\n\nВопрос: Что?\n\nОтвет: Да.",
        },
        {"invalid": "skipped"},
        {"full_text": ""},
    ]
    (tmp_path / CORPUS_JSON_NAME).write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )
    loader = CorpusLoader(tmp_path)
    docs = loader.load_documents()
    assert len(docs) == 1
    assert "Что?" in docs[0].page_content
    assert docs[0].metadata["source"] == CORPUS_JSON_NAME
    assert docs[0].metadata["url"] == "https://example.com"
