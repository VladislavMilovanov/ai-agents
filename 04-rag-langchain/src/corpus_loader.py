import json
import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

CORPUS_PDF_NAMES = (
    "ouk_potrebitelskiy_kredit_lph.pdf",
    "usl_r_vkladov.pdf",
)
CORPUS_JSON_NAME = "sberbank_help_documents.json"


class CorpusLoader:
    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir

    def load_documents(self) -> list[Document]:
        docs: list[Document] = []
        for name in CORPUS_PDF_NAMES:
            path = self._data_dir / name
            if not path.is_file():
                logger.warning("Corpus file missing, skipping: %s", path)
                continue
            loader = PyPDFLoader(str(path))
            docs.extend(loader.load())
        json_path = self._data_dir / CORPUS_JSON_NAME
        if not json_path.is_file():
            logger.warning("Corpus file missing, skipping: %s", json_path)
        else:
            docs.extend(self._load_json_faq(json_path))
        return docs

    def _load_json_faq(self, path: Path) -> list[Document]:
        raw = path.read_text(encoding="utf-8")
        items = json.loads(raw)
        out: list[Document] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            text = item.get("full_text") or ""
            if not text.strip():
                continue
            meta = {"source": path.name, "url": item.get("url", "")}
            out.append(Document(page_content=text, metadata=meta))
        return out
