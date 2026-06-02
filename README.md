# paperkb

`paperkb` is a Python CLI for managing a local knowledge base of research
papers. The tool will store each paper's PDF alongside YAML metadata, then
provide commands for listing, searching, showing, citing, and rebuilding the
local index.

Planned commands:

```bash
paperkb init
paperkb add <pdf_path> --title "Attention Is All You Need" --authors "Vaswani et al." --year 2017
paperkb list
paperkb search transformers
paperkb cite transformers
paperkb show <paper_id>
paperkb rebuild
```

The project is intended to be built with `uv`, `Typer`, `Rich`, `Pydantic`,
`PyYAML`, `RapidFuzz`, and optional PDF text extraction via `PyMuPDF`.
