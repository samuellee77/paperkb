import json
from pathlib import Path
from typing import Dict, List, Optional

from paperkb.config import INDEX_PATH
from paperkb.models import Paper
from paperkb.storage import init_library, load_papers


def extract_pdf_text(pdf_path: Optional[str], max_pages: Optional[int] = None) -> str:
    if not pdf_path:
        return ""
    path = Path(pdf_path)
    if not path.exists():
        return ""
    try:
        import fitz
    except ImportError:
        return ""

    try:
        with fitz.open(path) as document:
            page_count = len(document) if max_pages is None else min(len(document), max_pages)
            return "\n".join(document[index].get_text() for index in range(page_count))
    except Exception:
        return ""


def searchable_text(paper: Paper, include_pdf_text: bool = False) -> str:
    parts = [
        paper.title,
        " ".join(paper.authors),
        str(paper.year or ""),
        " ".join(paper.keywords),
        paper.abstract,
        paper.notes,
    ]
    if include_pdf_text:
        parts.append(extract_pdf_text(paper.pdf_path))
    return " ".join(part for part in parts if part).lower()


def build_index(include_pdf_text: bool = False) -> List[Dict[str, object]]:
    init_library()
    entries = [
        {
            "id": paper.id,
            "title": paper.title,
            "authors": paper.authors,
            "year": paper.year,
            "keywords": paper.keywords,
            "pdf_path": paper.pdf_path,
            "text": searchable_text(paper, include_pdf_text=include_pdf_text),
            "includes_pdf_text": include_pdf_text,
        }
        for paper in load_papers()
    ]
    INDEX_PATH.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    return entries


def load_index() -> List[Dict[str, object]]:
    init_library()
    if not INDEX_PATH.exists():
        return build_index()
    try:
        data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return build_index()
    if not isinstance(data, list):
        return build_index()
    return [entry for entry in data if isinstance(entry, dict)]
