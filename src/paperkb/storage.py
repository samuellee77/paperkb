from pathlib import Path
from shutil import copy2

import yaml

from paperkb.config import METADATA_DIR, PAPERS_DIR
from paperkb.models import Paper
from paperkb.utils import ensure_pdf, slugify


def init_library() -> None:
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)


def metadata_path(paper_id: str) -> Path:
    return METADATA_DIR / f"{paper_id}.yaml"


def next_paper_id(title: str, year: int | None) -> str:
    base = slugify("-".join(part for part in [title, str(year) if year else ""] if part))
    candidate = base
    counter = 2
    while metadata_path(candidate).exists():
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate


def write_paper(paper: Paper) -> None:
    init_library()
    metadata_path(paper.id).write_text(
        yaml.safe_dump(paper.model_dump(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def read_paper(path: Path) -> Paper:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Paper.model_validate(data)


def load_papers() -> list[Paper]:
    init_library()
    papers: list[Paper] = []
    for path in sorted(METADATA_DIR.glob("*.yaml")):
        papers.append(read_paper(path))
    return papers


def add_paper(
    pdf_path: Path,
    title: str,
    authors: list[str],
    year: int | None,
    keywords: list[str],
    abstract: str,
    notes: str,
) -> Paper:
    init_library()
    source_pdf = ensure_pdf(pdf_path)
    paper_id = next_paper_id(title, year)
    stored_pdf = PAPERS_DIR / f"{paper_id}.pdf"
    copy2(source_pdf, stored_pdf)

    paper = Paper(
        id=paper_id,
        title=title,
        authors=authors,
        year=year,
        keywords=keywords,
        abstract=abstract,
        notes=notes,
        pdf_path=str(stored_pdf),
    )
    write_paper(paper)
    return paper
