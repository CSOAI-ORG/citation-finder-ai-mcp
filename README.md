<div align="center">

# Citation Finder Ai MCP

**MCP server for citation finder ai mcp operations**

[![PyPI](https://img.shields.io/pypi/v/meok-citation-finder-ai-mcp)](https://pypi.org/project/meok-citation-finder-ai-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MEOK AI Labs](https://img.shields.io/badge/MEOK_AI_Labs-MCP_Server-purple)](https://meok.ai)

</div>

## Overview

Citation Finder Ai MCP provides AI-powered tools via the Model Context Protocol (MCP).

## Tools

| Tool | Description |
|------|-------------|
| `find_citations` | Search for academic citations by topic, title, or author. Returns structured res |
| `format_citation` | Format a citation in the specified style (apa, mla, chicago, bibtex, harvard). |
| `check_doi` | Validate a DOI format and return its resolution URL and metadata lookup link. |
| `generate_bibliography` | Generate a formatted bibliography from a JSON array of citation objects. Each ob |

## Installation

```bash
pip install meok-citation-finder-ai-mcp
```

## Usage with Claude Desktop

Add to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "citation-finder-ai": {
      "command": "python",
      "args": ["-m", "meok_citation_finder_ai_mcp.server"]
    }
  }
}
```

## Usage with FastMCP

```python
from mcp.server.fastmcp import FastMCP

# This server exposes 4 tool(s) via MCP
# See server.py for full implementation
```

## License

MIT © [MEOK AI Labs](https://meok.ai)
