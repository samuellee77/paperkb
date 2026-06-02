from rapidfuzz import fuzz, process

from paperkb.indexer import load_index


def search_papers(query: str, limit: int = 10) -> list[dict[str, object]]:
    entries = load_index()
    choices = {entry["id"]: str(entry["text"]) for entry in entries}
    matches = process.extract(
        query.lower(),
        choices,
        scorer=fuzz.WRatio,
        limit=limit,
        score_cutoff=20,
    )
    by_id = {entry["id"]: entry for entry in entries}
    results: list[dict[str, object]] = []
    for _text, score, paper_id in matches:
        entry = dict(by_id[paper_id])
        entry["score"] = round(score, 1)
        results.append(entry)
    return results
