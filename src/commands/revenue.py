"""Revenue command group - payment tracking, analytics, financial reports."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import typer
from rich.table import Table
from rich.panel import Panel

from src.core.console import console, info_panel, error_panel
from src.core.config import get_config

revenue_app = typer.Typer(help="Revenue: track payments, analytics, financial reports")


@revenue_app.command()
def dashboard():
    """Show revenue dashboard overview."""
    config = get_config()
    data_path = config.ensure_data_dir() / "revenue"
    data_path.mkdir(exist_ok=True)

    ledger_file = data_path / "ledger.json"
    entries = _load_ledger(ledger_file)

    total = sum(e.get("amount", 0) for e in entries)
    this_month = sum(
        e.get("amount", 0) for e in entries
        if e.get("date", "").startswith(datetime.now().strftime("%Y-%m"))
    )

    console.print(Panel(
        f"[bold]Total Revenue:[/bold] ${total:,.2f}\n"
        f"[bold]This Month:[/bold] ${this_month:,.2f}\n"
        f"[bold]Transactions:[/bold] {len(entries)}\n"
        f"[bold]Data:[/bold] {ledger_file}",
        title="Revenue Dashboard",
        border_style="green",
    ))

    if entries:
        table = Table(title="Recent Transactions (last 10)")
        table.add_column("Date", style="dim")
        table.add_column("Source", style="cyan")
        table.add_column("Amount", style="bold green", justify="right")
        table.add_column("Note", style="dim")

        for entry in entries[-10:]:
            table.add_row(
                entry.get("date", "?"),
                entry.get("source", "?"),
                f"${entry.get('amount', 0):,.2f}",
                entry.get("note", ""),
            )
        console.print(table)


@revenue_app.command()
def add(
    amount: float = typer.Argument(..., help="Transaction amount"),
    source: str = typer.Option("manual", "--source", "-s", help="Revenue source"),
    note: str = typer.Option("", "--note", "-n", help="Transaction note"),
):
    """Record a revenue transaction."""
    config = get_config()
    data_path = config.ensure_data_dir() / "revenue"
    data_path.mkdir(exist_ok=True)

    ledger_file = data_path / "ledger.json"
    entries = _load_ledger(ledger_file)

    entry = {
        "date": datetime.now().isoformat(),
        "amount": amount,
        "source": source,
        "note": note,
    }
    entries.append(entry)
    _save_ledger(ledger_file, entries)

    console.print(f"[green]Recorded:[/green] ${amount:,.2f} from {source}")


@revenue_app.command()
def report(
    period: str = typer.Option("month", "--period", "-p", help="Report period: week, month, year"),
):
    """Generate revenue report for a period."""
    config = get_config()
    data_path = config.ensure_data_dir() / "revenue"
    ledger_file = data_path / "ledger.json"
    entries = _load_ledger(ledger_file)

    if not entries:
        console.print("[yellow]No transactions recorded yet.[/yellow]")
        return

    now = datetime.now()
    if period == "week":
        cutoff = now.replace(day=max(1, now.day - 7))
    elif period == "year":
        cutoff = now.replace(month=1, day=1)
    else:
        cutoff = now.replace(day=1)

    cutoff_str = cutoff.isoformat()
    filtered = [e for e in entries if e.get("date", "") >= cutoff_str]

    total = sum(e.get("amount", 0) for e in filtered)

    # Group by source
    by_source: dict[str, float] = {}
    for e in filtered:
        src = e.get("source", "unknown")
        by_source[src] = by_source.get(src, 0) + e.get("amount", 0)

    table = Table(title=f"Revenue Report ({period})")
    table.add_column("Source", style="cyan")
    table.add_column("Amount", style="bold green", justify="right")
    table.add_column("Share", justify="right")

    for src, amt in sorted(by_source.items(), key=lambda x: -x[1]):
        share = (amt / total * 100) if total > 0 else 0
        table.add_row(src, f"${amt:,.2f}", f"{share:.1f}%")

    table.add_row("[bold]TOTAL[/bold]", f"[bold]${total:,.2f}[/bold]", "100%")
    console.print(table)


@revenue_app.command()
def export(
    format: str = typer.Option("csv", "--format", "-f", help="Export format: csv, json"),
    output: str = typer.Option("revenue-export", "--output", "-o", help="Output filename"),
):
    """Export revenue data."""
    config = get_config()
    data_path = config.ensure_data_dir() / "revenue"
    ledger_file = data_path / "ledger.json"
    entries = _load_ledger(ledger_file)

    if not entries:
        console.print("[yellow]No data to export.[/yellow]")
        return

    if format == "json":
        out_file = Path(f"{output}.json")
        out_file.write_text(json.dumps(entries, indent=2))
    else:
        out_file = Path(f"{output}.csv")
        lines = ["date,source,amount,note"]
        for e in entries:
            lines.append(f"{e.get('date', '')},{e.get('source', '')},{e.get('amount', 0)},{e.get('note', '')}")
        out_file.write_text("\n".join(lines))

    console.print(f"[green]Exported {len(entries)} entries to {out_file}[/green]")


def _load_ledger(path: Path) -> list[dict]:
    """Load ledger from JSON file."""
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, ValueError):
        return []


def _save_ledger(path: Path, entries: list[dict]) -> None:
    """Save ledger to JSON file."""
    path.write_text(json.dumps(entries, indent=2))
