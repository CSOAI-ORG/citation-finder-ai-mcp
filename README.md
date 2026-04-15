# Citation Finder AI MCP Server

> By [MEOK AI Labs](https://meok.ai) — Find and format academic citations in APA, MLA, Chicago, and BibTeX

## Installation

```bash
pip install citation-finder-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `format_citation`
Format a citation in a specified style (APA, MLA, Chicago, etc.).

**Parameters:**
- `title` (str): Work title
- `authors` (str): Author names
- `year` (int): Publication year
- `style` (str): Citation style (default 'apa')

### `generate_bibtex`
Generate a BibTeX entry from citation details.

**Parameters:**
- `title` (str): Work title
- `authors` (str): Author names
- `year` (int): Publication year
- `journal` (str): Journal name

### `parse_citation`
Parse a raw citation text into structured fields.

**Parameters:**
- `citation_text` (str): Raw citation text

### `validate_doi`
Validate a DOI (Digital Object Identifier).

**Parameters:**
- `doi` (str): DOI to validate

## Authentication

Free tier: 30 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
