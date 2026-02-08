"""Market command group - domain research, page analysis, competitor discovery."""

from __future__ import annotations

import re
import subprocess

import typer
from rich.panel import Panel
from rich.table import Table

from src.core.console import console, info_panel, error_panel

market_app = typer.Typer(help="Market: research, analyze, competitors")


def _run_cmd(args: list[str], timeout: int = 10) -> str:
    """Run a subprocess command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except FileNotFoundError:
        return ""
    except subprocess.TimeoutExpired:
        return ""


@market_app.command()
def research(
    domain: str = typer.Argument(..., help="Domain to research (e.g. example.com)"),
) -> None:
    """Research a domain: DNS records, server info, HTTP headers."""
    info_panel("Domain Research", f"Researching: {domain}")

    # DNS lookup
    dns_output = _run_cmd(["dig", "+short", domain]) or _run_cmd(["nslookup", domain])
    dns_summary = dns_output.split("\n")[0] if dns_output else "unavailable"

    # HTTP headers
    header_output = _run_cmd(["curl", "-sI", f"https://{domain}"], timeout=15)
    server = ""
    tech_hints: list[str] = []
    status_line = ""

    for line in header_output.split("\n"):
        lower = line.lower()
        if lower.startswith("http/"):
            status_line = line.strip()
        elif lower.startswith("server:"):
            server = line.split(":", 1)[1].strip()
        elif lower.startswith("x-powered-by:"):
            tech_hints.append(line.split(":", 1)[1].strip())
        elif lower.startswith("set-cookie:") and "platform" in lower:
            tech_hints.append("cookie-platform-detected")

    table = Table(title=f"Domain Research: {domain}")
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Domain", domain)
    table.add_row("DNS (A record)", dns_summary)
    table.add_row("HTTP Status", status_line or "no response")
    table.add_row("Server", server or "not disclosed")
    table.add_row("Tech Hints", ", ".join(tech_hints) if tech_hints else "none detected")

    console.print(table)


@market_app.command()
def analyze(
    url: str = typer.Argument(..., help="URL to analyze (e.g. https://example.com)"),
) -> None:
    """Quick page analysis: title, size, status, element counts."""
    info_panel("Page Analysis", f"Fetching: {url}")

    body = _run_cmd(["curl", "-sL", "-w", "\n%{http_code}", url], timeout=20)
    if not body:
        error_panel("Fetch Failed", f"Could not reach {url}")
        raise typer.Exit(code=1)

    lines = body.rsplit("\n", 1)
    html = lines[0] if len(lines) == 2 else body
    status_code = lines[1] if len(lines) == 2 else "unknown"

    # Extract title
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1).strip() if title_match else "no title"

    # Count elements
    divs = len(re.findall(r"<div[\s>]", html, re.IGNORECASE))
    links = len(re.findall(r"<a[\s>]", html, re.IGNORECASE))
    images = len(re.findall(r"<img[\s>]", html, re.IGNORECASE))
    scripts = len(re.findall(r"<script[\s>]", html, re.IGNORECASE))

    size_kb = len(html.encode("utf-8", errors="replace")) / 1024

    content = (
        f"[bold]Title:[/bold] {title}\n"
        f"[bold]Status:[/bold] {status_code}\n"
        f"[bold]Size:[/bold] {size_kb:.1f} KB\n\n"
        f"[bold]Elements:[/bold]\n"
        f"  divs: {divs}  |  links: {links}  |  images: {images}  |  scripts: {scripts}"
    )
    console.print(Panel(content, title=f"Page Analysis: {url}", border_style="cyan"))


@market_app.command()
def competitors(
    domain: str = typer.Argument(..., help="Domain to find competitors for"),
) -> None:
    """Suggest competitor discovery queries for a domain."""
    info_panel("Competitor Discovery", f"Analyzing: {domain}")

    # Extract meaningful parts from the domain
    parts = domain.replace("www.", "").split(".")
    name = parts[0] if parts else domain
    tld = parts[-1] if len(parts) > 1 else "com"

    queries = [
        f'"{name}" alternatives',
        f'"{name}" vs competitors',
        f"best {name} alternatives {tld.upper()} market",
        f"sites like {domain}",
        f'"{name}" competitor analysis',
    ]

    content = (
        f"[bold]Domain:[/bold] {domain}\n"
        f"[bold]Brand:[/bold] {name}\n\n"
        f"[bold]Suggested Search Queries:[/bold]\n"
    )
    for i, q in enumerate(queries, 1):
        content += f"  {i}. {q}\n"

    content += (
        "\n[bold]Next Steps:[/bold]\n"
        "  - Run queries in your preferred search engine\n"
        "  - Use [cyan]mekon market research <competitor-domain>[/cyan] on each result\n"
        "  - Use [cyan]mekon market analyze <competitor-url>[/cyan] for page insights"
    )
    console.print(Panel(content, title=f"Competitors: {domain}", border_style="magenta"))
