import json

from paperkb.config import INDEX_PATH
from paperkb.models import Paper
from paperkb.storage import init_library, load_papers


def searchable_text(paper: Paper) -> str:
    parts = [
        paper.title,
        " ".join(paper.authors),
        str(paper.year or ""),
        " ".join(paper.keywords),
        paper.abstract,
        paper.notes,
    ]
    return " ".join(part for part in parts if part).lower()


def build_index() -> list[dict[str, object]]:
    init_library()
    entries = [
        {
            "id": paper.id,
            "title": paper.title,
            "authors": paper.authors,
            "year": paper.year,
            "keywords": paper.keywords,
            "pdf_path": paper.pdf_path,
            "text": searchable_text(paper),
        }
        for paper in load_papers()
    ]
    INDEX_PATH.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    return entries
