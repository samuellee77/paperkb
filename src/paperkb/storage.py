from pathlib import Path
from shutil import copy2
from typing import Any, Dict, List, Optional

import json
import yaml

from paperkb.config import DEMO_PAPER_ID, DEMO_PAPER_SOURCE, METADATA_DIR, PAPERS_DIR
from paperkb.models import Paper
from paperkb.utils import ensure_pdf, slugify


def init_library() -> None:
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)


def metadata_path(paper_id: str) -> Path:
    return METADATA_DIR / f"{paper_id}.yaml"


def next_paper_id(title: str, year: Optional[int]) -> str:
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


def load_papers() -> List[Paper]:
    init_library()
    papers: List[Paper] = []
    for path in sorted(METADATA_DIR.glob("*.yaml")):
        papers.append(read_paper(path))
    return papers


def get_paper(paper_id: str) -> Optional[Paper]:
    path = metadata_path(paper_id)
    if not path.exists():
        return None
    return read_paper(path)


def add_paper(
    pdf_path: Path,
    title: str,
    authors: List[str],
    year: Optional[int],
    keywords: List[str],
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


def add_paper_from_data(data: Dict[str, Any], pdf_path: Optional[Path] = None) -> Paper:
    template_pdf_path = str(data.get("pdf_path") or "").strip()
    selected_pdf_path = pdf_path or (Path(template_pdf_path) if template_pdf_path else None)
    if selected_pdf_path is None:
        raise ValueError("Template must include pdf_path, or pass a PDF path to `paperkb add`.")
    if "title" not in data:
        raise ValueError("Template must include title.")

    return add_paper(
        pdf_path=selected_pdf_path,
        title=str(data["title"]),
        authors=_list_field(data.get("authors")),
        year=_optional_int(data.get("year")),
        keywords=_list_field(data.get("keywords")),
        abstract=str(data.get("abstract") or ""),
        notes=str(data.get("notes") or ""),
    )


def load_add_template(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON template must be an object.")
        return data
    if path.suffix.lower() in {".txt", ".text"}:
        return _parse_text_template(path.read_text(encoding="utf-8"))
    raise ValueError("Template must be a .json or .txt file.")


def template_data() -> Dict[str, Any]:
    return {
        "pdf_path": "./paper.pdf",
        "title": "Paper Title",
        "authors": ["Author One", "Author Two"],
        "year": 2026,
        "keywords": ["keyword one", "keyword two"],
        "abstract": "Short paper abstract.",
        "notes": "Personal notes for this paper.",
    }


def write_add_template(path: Path, template_format: str) -> Path:
    if template_format not in {"json", "txt"}:
        raise ValueError("Template format must be json or txt.")
    if path.exists():
        raise FileExistsError(f"Template already exists: {path}")

    data = template_data()
    if template_format == "json":
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    else:
        path.write_text(_format_text_template(data), encoding="utf-8")
    return path


def _parse_text_template(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    current_key: Optional[str] = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            current_key = key.strip()
            data[current_key] = value.strip()
        elif current_key:
            data[current_key] = f"{data[current_key]}\n{line.strip()}".strip()
    return data


def _format_text_template(data: Dict[str, Any]) -> str:
    return (
        "# Edit this file, then run: paperkb add --from-file paper.txt\n"
        f"pdf_path: {data['pdf_path']}\n"
        f"title: {data['title']}\n"
        f"authors: {', '.join(data['authors'])}\n"
        f"year: {data['year']}\n"
        f"keywords: {', '.join(data['keywords'])}\n"
        f"abstract: {data['abstract']}\n"
        f"notes: {data['notes']}\n"
    )


def _list_field(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _optional_int(value: Any) -> Optional[int]:
    if value in {None, ""}:
        return None
    return int(value)


def seed_demo_paper() -> Optional[Paper]:
    init_library()
    demo_metadata = metadata_path(DEMO_PAPER_ID)
    if demo_metadata.exists():
        return read_paper(demo_metadata)
    if not DEMO_PAPER_SOURCE.exists():
        return None

    stored_pdf = PAPERS_DIR / f"{DEMO_PAPER_ID}.pdf"
    copy2(DEMO_PAPER_SOURCE, stored_pdf)

    paper = Paper(
        id=DEMO_PAPER_ID,
        title="A Mechanistic Explanation for the Inverted Face Effect",
        authors=[
            "Alex Tahan",
            "Hsin-Yuan Lee",
            "Kira Fleischer",
            "Nikita Kachappilly",
            "Xavier Chen",
            "Garrison W. Cottrell",
        ],
        year=2026,
        keywords=[
            "Inverted Face Effect",
            "Face Processing",
            "Biologically Plausible Models",
            "log-polar mapping",
            "foveated retina",
        ],
        abstract=(
            "Presents a mechanistic account of the Inverted Face Effect using "
            "multiple fixations, salience-driven sampling, a foveated retina, "
            "and log-polar mapping from the visual field to V1."
        ),
        notes="Demo seed paper created by `paperkb init`.",
        pdf_path=str(stored_pdf),
        citation="Tahan, Lee, Fleischer, Kachappilly, Chen, & Cottrell (2026)",
    )
    write_paper(paper)
    return paper
