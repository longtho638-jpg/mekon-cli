"""Shared Rich console instance and formatting helpers."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def success_panel(title: str, message: str) -> None:
    """Display a success panel."""
    console.print(Panel(Text(message, style="bold green"), title=title, border_style="green"))


def error_panel(title: str, message: str) -> None:
    """Display an error panel."""
    console.print(Panel(Text(message, style="bold red"), title=title, border_style="red"))


def info_panel(title: str, message: str) -> None:
    """Display an info panel."""
    console.print(Panel(message, title=title, border_style="cyan"))


def status_table(title: str, rows: list[dict[str, str]], columns: list[str]) -> None:
    """Display a formatted status table."""
    table = Table(title=title)
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*[row.get(col, "") for col in columns])
    console.print(table)
