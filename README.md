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

- `paperkb init`
- `paperkb add`
- `paperkb template`
- `paperkb list`
- `paperkb search`
- `paperkb cite`
- `paperkb show`
- `paperkb rebuild`
