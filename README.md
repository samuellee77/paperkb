# paperkb

`paperkb` is a Python CLI for managing a local knowledge base of research
papers. It stores PDFs in `data/papers/`, writes YAML metadata to
`data/metadata/`, and builds a local `data/index.json` for search.

## Install

From a local checkout:

```bash
uv sync
uv run paperkb --help
```

From GitHub:

```bash
uv add "git+https://github.com/samuellee77/paperkb.git"
```

## Usage

Initialize the local library:

```bash
uv run paperkb init
```

Add a paper:

```bash
uv run paperkb add ./attention.pdf \
  --title "Attention Is All You Need" \
  --authors "Vaswani et al." \
  --year 2017 \
  --keywords "transformer,attention,NLP" \
  --abstract "Introduces the Transformer architecture." \
  --notes "Useful baseline citation for sequence modeling."
```

Or generate a template, edit it, and add from the file:

```bash
uv run paperkb template paper.json
uv run paperkb add --from-file paper.json
```

TXT templates are also supported:

```bash
uv run paperkb template paper.txt --format txt
uv run paperkb add --from-file paper.txt
```

The template file can include `pdf_path`, or you can pass a PDF path to override
the file:

```bash
uv run paperkb add ./attention.pdf --from-file paper.json
```

List papers:

```bash
uv run paperkb list
```

Search papers:

```bash
uv run paperkb search "transformer attention"
```

Print the best matching citation:

```bash
uv run paperkb cite "face inversion effect"
```

Show full metadata:

```bash
uv run paperkb show demo-ife-paper
```

Rebuild the search index:

```bash
uv run paperkb rebuild
uv run paperkb rebuild --include-pdf-text
```

## Commands

### `paperkb init`

Creates the local knowledge base folders and search index.

```bash
uv run paperkb init
```

This creates `data/papers/` for stored PDF files, `data/metadata/` for YAML
metadata files, and `data/index.json` for search. It also seeds the library with
the included demo Inverted Face Effect paper if `demo_ife_paper.pdf` is present.

### `paperkb template`

Creates an editable metadata template so you do not have to type every field in
the terminal.

```bash
uv run paperkb template paper.json
```

You can also create a plain text template:

```bash
uv run paperkb template paper.txt --format txt
```

After editing the file, use it with `paperkb add --from-file`.

### `paperkb add`

Adds a paper to the knowledge base. It copies the PDF into `data/papers/`,
writes YAML metadata into `data/metadata/`, and rebuilds the search index.

You can add a paper directly from the terminal:

```bash
uv run paperkb add ./attention.pdf \
  --title "Attention Is All You Need" \
  --authors "Vaswani et al." \
  --year 2017 \
  --keywords "transformer,attention,NLP" \
  --abstract "Introduces the Transformer architecture." \
  --notes "Useful baseline citation for sequence modeling."
```

Or add from a JSON/TXT template:

```bash
uv run paperkb add --from-file paper.json
```

If the template does not include `pdf_path`, pass the PDF path separately:

```bash
uv run paperkb add ./attention.pdf --from-file paper.json
```

### `paperkb list`

Shows all papers currently in the local library.

```bash
uv run paperkb list
```

The output includes each paper's ID, title, year, authors, and keywords.

### `paperkb search`

Searches the knowledge base for papers matching a query.

```bash
uv run paperkb search "face inversion effect"
```

Search uses fuzzy matching over paper titles, authors, years, keywords,
abstracts, notes, and any PDF text included by
`paperkb rebuild --include-pdf-text`.

### `paperkb cite`

Finds the best matching paper for a query and prints a citation.

```bash
uv run paperkb cite "log-polar mapping"
```

This is useful when you remember a topic or keyword but not the exact paper ID.
It also prints the matched PDF path when available.

### `paperkb show`

Displays full metadata for one paper.

```bash
uv run paperkb show demo-ife-paper
```

Use this when you want to inspect the complete title, authors, year, keywords,
abstract, notes, PDF path, and citation for a specific paper.

### `paperkb rebuild`

Rebuilds the local search index from the YAML metadata files.

```bash
uv run paperkb rebuild
```

Use this if metadata files were edited manually.

To also extract searchable text from PDFs, run:

```bash
uv run paperkb rebuild --include-pdf-text
```

This uses PyMuPDF to read PDF text and include it in `data/index.json`.
