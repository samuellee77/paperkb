from paperkb.models import Paper
from paperkb.search import search_papers
from paperkb.storage import get_paper


def format_citation(paper: Paper) -> str:
    if paper.citation:
        return paper.citation
    author_text = ", ".join(paper.authors) if paper.authors else "Unknown author"
    year_text = str(paper.year) if paper.year else "n.d."
    return f"{author_text} ({year_text}). {paper.title}."


def citation_match(query: str) -> tuple[Paper, dict[str, object]] | None:
    results = search_papers(query, limit=1)
    if not results:
        return None
    paper = get_paper(str(results[0]["id"]))
    if paper is None:
        return None
    return paper, results[0]


def matched_keywords(paper: Paper, query: str) -> list[str]:
    query_lower = query.lower()
    return [keyword for keyword in paper.keywords if keyword.lower() in query_lower]
