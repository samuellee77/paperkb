from paperkb.models import Paper


def format_citation(paper: Paper) -> str:
    author_text = ", ".join(paper.authors) if paper.authors else "Unknown author"
    year_text = str(paper.year) if paper.year else "n.d."
    return f"{author_text} ({year_text}). {paper.title}."
