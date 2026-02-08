"""Logs command group - view and manage activity logs."""

from __future__ import annotations

import typer
from rich.table import Table

from src.core.console import console, success_panel
from src.core.logger import get_logger

logs_app = typer.Typer(help="Activity log management")


@logs_app.command()
def show(
    limit: int = typer.Option(50, "--limit", "-n", help="Number of entries to show"),
) -> None:
    """Show recent activity log entries."""
    logger = get_logger()
    entries = logger.read(limit=limit)

    if not entries:
        console.print("[dim]No log entries found.[/dim]")
        return

    table = Table(title=f"Activity Log (last {len(entries)})")
    table.add_column("Timestamp", style="dim")
    table.add_column("Action", style="cyan")
    table.add_column("Details")
    table.add_column("Status", style="green")

    for entry in entries:
        ts = entry.get("timestamp", "")
        # Trim microseconds for readability
        if "." in ts:
            ts = ts.split(".")[0]
        table.add_row(
            ts,
            entry.get("action", ""),
            entry.get("details", ""),
            entry.get("status", ""),
        )

    console.print(table)


@logs_app.command()
def tail() -> None:
    """Show last 10 log entries."""
    logger = get_logger()
    entries = logger.read(limit=10)

    if not entries:
        console.print("[dim]No log entries found.[/dim]")
        return

    table = Table(title="Activity Log (tail)")
    table.add_column("Timestamp", style="dim")
    table.add_column("Action", style="cyan")
    table.add_column("Details")
    table.add_column("Status", style="green")

    for entry in entries:
        ts = entry.get("timestamp", "")
        if "." in ts:
            ts = ts.split(".")[0]
        table.add_row(
            ts,
            entry.get("action", ""),
            entry.get("details", ""),
            entry.get("status", ""),
        )

    console.print(table)


@logs_app.command()
def clear() -> None:
    """Clear all activity logs."""
    typer.confirm("Clear all activity logs?", abort=True)
    logger = get_logger()
    count = logger.clear()
    success_panel("Logs Cleared", f"Removed {count} log entries.")
