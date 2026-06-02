from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from paperkb.citation import citation_match, format_citation, matched_keywords
from paperkb.indexer import build_index
from paperkb.search import search_papers
from paperkb.storage import add_paper, get_paper, init_library, load_papers, metadata_path, seed_demo_paper
from paperkb.utils import parse_csv

app = typer.Typer(help="Manage a local knowledge base of research papers.")
console = Console()


@app.command()
def init() -> None:
    """Create the local data directories and seed the demo IFE paper."""
    init_library()
    had_demo = metadata_path("demo-ife-paper").exists()
    demo_paper = seed_demo_paper()
    build_index()
    console.print("[green]Initialized paperkb library in ./data[/green]")
    if demo_paper and not had_demo:
        console.print(f"[green]Seeded demo paper[/green] {demo_paper.id}")
    elif demo_paper:
        console.print(f"[cyan]Demo paper already exists[/cyan] {demo_paper.id}")
    else:
        console.print("[yellow]Demo paper not found: demo_ife_paper.pdf[/yellow]")


@app.command("add")
def add_command(
    pdf_path: Annotated[Path, typer.Argument(help="Path to the PDF to add.")],
    title: Annotated[str, typer.Option("--title", "-t", help="Paper title.")],
    authors: Annotated[str, typer.Option("--authors", "-a", help="Comma-separated authors.")] = "",
    year: Annotated[int | None, typer.Option("--year", "-y", help="Publication year.")] = None,
    keywords: Annotated[str, typer.Option("--keywords", "-k", help="Comma-separated keywords.")] = "",
    abstract: Annotated[str, typer.Option("--abstract", help="Paper abstract.")] = "",
    notes: Annotated[str, typer.Option("--notes", "-n", help="Personal notes.")] = "",
) -> None:
    """Copy a PDF into the library and write YAML metadata."""
    try:
        paper = add_paper(
            pdf_path=pdf_path,
            title=title,
            authors=parse_csv(authors),
            year=year,
            keywords=parse_csv(keywords),
            abstract=abstract,
            notes=notes,
        )
    except (FileNotFoundError, ValueError) as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    build_index()
    console.print(f"[green]Added[/green] {paper.id}")


@app.command("list")
def list_command() -> None:
    """List papers in the local library."""
    papers = load_papers()
    if not papers:
        console.print("[yellow]No papers found. Add one with `paperkb add`.[/yellow]")
        return

    table = Table(title="Papers")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Year", justify="right")
    table.add_column("Authors")
    table.add_column("Keywords")

    for paper in papers:
        table.add_row(
            paper.id,
            paper.title,
            str(paper.year or ""),
            ", ".join(paper.authors),
            ", ".join(paper.keywords),
        )

    console.print(table)


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query.")],
    limit: Annotated[int, typer.Option("--limit", "-l", min=1, help="Maximum results.")] = 10,
) -> None:
    """Search paper metadata and notes."""
    results = search_papers(query, limit=limit)
    if not results:
        console.print("[yellow]No matches found.[/yellow]")
        return

    table = Table(title=f"Search results for {query!r}")
    table.add_column("Score", justify="right")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Year", justify="right")
    table.add_column("Keywords")

    for result in results:
        table.add_row(
            str(result["score"]),
            str(result["id"]),
            str(result["title"]),
            str(result["year"] or ""),
            ", ".join(result["keywords"]),
        )

    console.print(table)


@app.command()
def cite(query: Annotated[str, typer.Argument(help="Search query for the paper to cite.")]) -> None:
    """Find the best matching paper and print its citation."""
    match = citation_match(query)
    if match is None:
        console.print("[yellow]No citation match found.[/yellow]")
        raise typer.Exit(code=1)

    paper, result = match
    keywords = matched_keywords(paper, query)
    reason = ", ".join(keywords) if keywords else f"fuzzy score {result['score']}"

    console.print(Panel(format_citation(paper), title="Best citation", border_style="green"))
    console.print(f"[bold]Reason:[/bold] {reason}")
    if paper.pdf_path:
        console.print(f"[bold]PDF:[/bold] {paper.pdf_path}")


@app.command()
def show(paper_id: Annotated[str, typer.Argument(help="Paper ID to show.")]) -> None:
    """Show full metadata for one paper."""
    paper = get_paper(paper_id)
    if paper is None:
        console.print(f"[red]Paper not found:[/red] {paper_id}")
        raise typer.Exit(code=1)

    table = Table(title=paper.id, show_header=False)
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("Title", paper.title)
    table.add_row("Authors", "\n".join(paper.authors))
    table.add_row("Year", str(paper.year or ""))
    table.add_row("Keywords", ", ".join(paper.keywords))
    table.add_row("Abstract", paper.abstract)
    table.add_row("Notes", paper.notes)
    table.add_row("PDF", paper.pdf_path or "")
    table.add_row("Citation", format_citation(paper))
    console.print(table)


@app.command()
def rebuild(
    include_pdf_text: Annotated[
        bool,
        typer.Option("--include-pdf-text", help="Extract PDF text into the search index."),
    ] = False,
) -> None:
    """Rebuild the local search index."""
    entries = build_index(include_pdf_text=include_pdf_text)
    suffix = " with PDF text" if include_pdf_text else ""
    console.print(f"[green]Rebuilt index{suffix}:[/green] {len(entries)} papers")
