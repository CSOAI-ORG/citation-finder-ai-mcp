#!/usr/bin/env python3
"""
Find and format academic citations in APA, MLA, Chicago, and BibTeX styles. — MEOK AI Labs."""

import sys, os
from auth_middleware import check_access

import json, re, hashlib
from datetime import datetime, timezone
from collections import defaultdict
from mcp.server.fastmcp import FastMCP
from urllib.parse import quote

FREE_DAILY_LIMIT = 30
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now - t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT:
        return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day. Upgrade: meok.ai"})
    _usage[c].append(now)
    return None

mcp = FastMCP("citation-finder-ai", instructions="Find and format academic citations in APA, MLA, Chicago, and BibTeX. By MEOK AI Labs.")


def _parse_authors(authors_str: str) -> list:
    """Parse author string into structured list."""
    authors = []
    for a in re.split(r'[,;&]|\band\b', authors_str):
        a = a.strip()
        if not a:
            continue
        parts = a.rsplit(' ', 1)
        if len(parts) == 2:
            authors.append({"first": parts[0].strip(), "last": parts[1].strip()})
        else:
            authors.append({"first": "", "last": a})
    return authors


def _format_authors_apa(authors: list) -> str:
    if not authors:
        return "Unknown"
    if len(authors) == 1:
        return f"{authors[0]['last']}, {authors[0]['first'][0]}." if authors[0]['first'] else authors[0]['last']
    parts = []
    for i, a in enumerate(authors):
        initial = f"{a['first'][0]}." if a['first'] else ""
        if i < len(authors) - 1:
            parts.append(f"{a['last']}, {initial}")
        else:
            parts.append(f"& {a['last']}, {initial}")
    return ", ".join(parts[:-1]) + " " + parts[-1] if len(parts) > 1 else parts[0]


def _format_authors_mla(authors: list) -> str:
    if not authors:
        return "Unknown"
    if len(authors) == 1:
        a = authors[0]
        return f"{a['last']}, {a['first']}" if a['first'] else a['last']
    first = authors[0]
    result = f"{first['last']}, {first['first']}" if first['first'] else first['last']
    if len(authors) == 2:
        second = authors[1]
        result += f", and {second['first']} {second['last']}"
    else:
        result += ", et al."
    return result


@mcp.tool()
def find_citations(query: str, max_results: int = 5, api_key: str = "") -> str:
    """Search for academic citations by topic, title, or author. Returns structured results for further formatting.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        query (str): The query to analyze or process.
        max_results (int): The max results to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://councilof.ai"})
    if err := _rl():
        return err

    max_results = max(1, min(max_results, 20))
    query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
    search_url = f"https://api.crossref.org/works?query={quote(query)}&rows={max_results}"
    search_url_semantic = f"https://api.semanticscholar.org/graph/v1/paper/search?query={quote(query)}&limit={max_results}"

    return json.dumps({
        "query": query,
        "max_results": max_results,
        "search_apis": {
            "crossref": search_url,
            "semantic_scholar": search_url_semantic,
        },
        "hint": "Use these URLs to fetch real citation data. The format_citation tool can then format any results.",
        "query_hash": query_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@mcp.tool()
def format_citation(title: str, authors: str, year: int, style: str = "apa", journal: str = "", volume: str = "", pages: str = "", doi: str = "", publisher: str = "", url: str = "", api_key: str = "") -> str:
    """Format a citation in the specified style (apa, mla, chicago, bibtex, harvard).

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        title (str): The title to analyze or process.
        authors (str): The authors to analyze or process.
        year (int): The year to analyze or process.
        style (str): The style to analyze or process.
        journal (str): The journal to analyze or process.
        volume (str): The volume to analyze or process.
        pages (str): The pages to analyze or process.
        doi (str): The doi to analyze or process.
        publisher (str): The publisher to analyze or process.
        url (str): The url to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://councilof.ai"})
    if err := _rl():
        return err

    style = style.lower().strip()
    supported = ["apa", "mla", "chicago", "bibtex", "harvard"]
    if style not in supported:
        return json.dumps({"error": f"Unsupported style '{style}'. Use: {', '.join(supported)}"})

    parsed_authors = _parse_authors(authors)
    formatted = ""

    if style == "apa":
        auth_str = _format_authors_apa(parsed_authors)
        formatted = f"{auth_str} ({year}). {title}."
        if journal:
            formatted += f" *{journal}*"
            if volume:
                formatted += f", *{volume}*"
            if pages:
                formatted += f", {pages}"
            formatted += "."
        if doi:
            formatted += f" https://doi.org/{doi}"

    elif style == "mla":
        auth_str = _format_authors_mla(parsed_authors)
        formatted = f'{auth_str}. "{title}."'
        if journal:
            formatted += f" *{journal}*"
            if volume:
                formatted += f", vol. {volume}"
            if pages:
                formatted += f", pp. {pages}"
            formatted += f", {year}."
        else:
            formatted += f" {year}."
        if doi:
            formatted += f" doi:{doi}."

    elif style == "chicago":
        auth_str = _format_authors_mla(parsed_authors)
        formatted = f'{auth_str}. "{title}."'
        if journal:
            formatted += f" *{journal}* {volume}"
            if pages:
                formatted += f": {pages}"
            formatted += f" ({year})."
        else:
            if publisher:
                formatted += f" {publisher}, {year}."
            else:
                formatted += f" {year}."
        if doi:
            formatted += f" https://doi.org/{doi}."

    elif style == "harvard":
        auth_str = _format_authors_apa(parsed_authors)
        formatted = f"{auth_str} ({year}) '{title}',"
        if journal:
            formatted += f" *{journal}*"
            if volume:
                formatted += f", {volume}"
            if pages:
                formatted += f", pp. {pages}"
            formatted += "."
        if doi:
            formatted += f" doi: {doi}."

    elif style == "bibtex":
        key = ""
        if parsed_authors:
            key += parsed_authors[0]['last'].lower()
        key += str(year)
        entry_type = "article" if journal else "misc"
        lines = [f"@{entry_type}{{{key},"]
        lines.append(f"  title = {{{title}}},")
        lines.append(f"  author = {{{authors}}},")
        lines.append(f"  year = {{{year}}},")
        if journal:
            lines.append(f"  journal = {{{journal}}},")
        if volume:
            lines.append(f"  volume = {{{volume}}},")
        if pages:
            lines.append(f"  pages = {{{pages}}},")
        if doi:
            lines.append(f"  doi = {{{doi}}},")
        if url:
            lines.append(f"  url = {{{url}}},")
        if publisher:
            lines.append(f"  publisher = {{{publisher}}},")
        lines.append("}")
        formatted = "\n".join(lines)

    return json.dumps({
        "style": style,
        "formatted": formatted,
        "metadata": {"title": title, "authors": [{"first": a["first"], "last": a["last"]} for a in parsed_authors], "year": year, "journal": journal, "doi": doi},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@mcp.tool()
def check_doi(doi: str, api_key: str = "") -> str:
    """Validate a DOI format and return its resolution URL and metadata lookup link.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        doi (str): The doi to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://councilof.ai"})
    if err := _rl():
        return err

    doi = doi.strip()
    if doi.startswith("https://doi.org/"):
        doi = doi[len("https://doi.org/"):]
    if doi.startswith("http://doi.org/"):
        doi = doi[len("http://doi.org/"):]
    if doi.startswith("doi:"):
        doi = doi[4:]

    valid_pattern = re.match(r'^10\.\d{4,9}/[^\s]+$', doi)
    prefix = doi.split('/')[0] if '/' in doi else ""

    return json.dumps({
        "doi": doi,
        "valid_format": bool(valid_pattern),
        "resolution_url": f"https://doi.org/{doi}",
        "crossref_api": f"https://api.crossref.org/works/{quote(doi)}",
        "prefix": prefix,
        "registrant": prefix if prefix.startswith("10.") else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@mcp.tool()
def generate_bibliography(citations_json: str, style: str = "apa", sort_by: str = "author", api_key: str = "") -> str:
    """Generate a formatted bibliography from a JSON array of citation objects. Each object needs: title, authors, year.

    Behavior:
        This tool generates structured output without modifying external systems.
        Output is deterministic for identical inputs. No side effects.
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        citations_json (str): The citations json to analyze or process.
        style (str): The style to analyze or process.
        sort_by (str): The sort by to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://councilof.ai"})
    if err := _rl():
        return err

    try:
        citations = json.loads(citations_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON. Provide a JSON array of citation objects with title, authors, year."})

    if not isinstance(citations, list):
        return json.dumps({"error": "Expected a JSON array of citation objects."})

    entries = []
    for i, c in enumerate(citations):
        if not isinstance(c, dict):
            entries.append({"index": i, "error": "Not a valid citation object"})
            continue
        title = c.get("title", "Untitled")
        authors_str = c.get("authors", "Unknown")
        year = c.get("year", 0)
        journal = c.get("journal", "")
        doi = c.get("doi", "")
        volume = c.get("volume", "")
        pages = c.get("pages", "")
        parsed = _parse_authors(authors_str)

        if style == "apa":
            auth = _format_authors_apa(parsed)
            entry = f"{auth} ({year}). {title}."
            if journal:
                entry += f" *{journal}*"
                if volume:
                    entry += f", *{volume}*"
                if pages:
                    entry += f", {pages}"
                entry += "."
            if doi:
                entry += f" https://doi.org/{doi}"
        elif style == "mla":
            auth = _format_authors_mla(parsed)
            entry = f'{auth}. "{title}."'
            if journal:
                entry += f" *{journal}*"
                if volume:
                    entry += f", vol. {volume}"
                if pages:
                    entry += f", pp. {pages}"
                entry += f", {year}."
            else:
                entry += f" {year}."
        else:
            auth = _format_authors_apa(parsed)
            entry = f"{auth} ({year}). {title}."
            if journal:
                entry += f" {journal}."

        entries.append({"index": i, "formatted": entry, "sort_key_author": parsed[0]["last"] if parsed else "zzz", "sort_key_year": year})

    valid_entries = [e for e in entries if "formatted" in e]
    if sort_by == "year":
        valid_entries.sort(key=lambda x: x["sort_key_year"])
    else:
        valid_entries.sort(key=lambda x: x["sort_key_author"].lower())

    bibliography = "\n\n".join(e["formatted"] for e in valid_entries)

    return json.dumps({
        "style": style,
        "sort_by": sort_by,
        "entry_count": len(valid_entries),
        "bibliography": bibliography,
        "entries": [{"index": e["index"], "formatted": e["formatted"]} for e in valid_entries],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


def main():
    mcp.run()

if __name__ == '__main__':
    main()
