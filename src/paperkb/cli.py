from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from paperkb.indexer import build_index
from paperkb.search import search_papers
from paperkb.storage import add_paper, init_library, load_papers
from paperkb.utils import parse_csv

app = typer.Typer(help="Manage a local knowledge base of research papers.")
console = Console()


@app.command()
def init() -> None:
    """Create the local data directories."""
    init_library()
    build_index()
    console.print("[green]Initialized paperkb library in ./data[/green]")


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
