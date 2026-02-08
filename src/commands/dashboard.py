"""Interactive terminal dashboard command.

Displays a 4-panel grid with DevOps, Revenue, Agents, System status.
Uses Rich Layout + Live display with keyboard navigation.
"""

from __future__ import annotations

import sys
import time
import threading

import typer
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

from src.core.console import console
from src.core.collectors import (
    collect_devops,
    collect_revenue,
    collect_agents,
    collect_system,
)


def _build_layout(focused: int = 0) -> Layout:
    """Build the dashboard layout. If focused > 0, expand that panel."""
    panels = {
        1: collect_devops,
        2: collect_revenue,
        3: collect_agents,
        4: collect_system,
    }

    # Focused mode: show single panel expanded
    if focused in panels:
        layout = Layout()
        layout.split_column(
            Layout(name="main", ratio=8),
            Layout(name="footer", size=3),
        )
        layout["main"].update(panels[focused]())
        layout["footer"].update(Panel(
            "[bold]q[/bold] Quit  [bold]r[/bold] Refresh  "
            "[bold]0[/bold] Grid view  "
            f"[bold]1-4[/bold] Focus panel  [dim]Viewing: {focused}[/dim]",
            style="dim",
        ))
        return layout

    # Grid mode: 2x2 panels
    layout = Layout()
    layout.split_column(
        Layout(name="top", ratio=4),
        Layout(name="bottom", ratio=4),
        Layout(name="footer", size=3),
    )
    layout["top"].split_row(
        Layout(name="devops"),
        Layout(name="revenue"),
    )
    layout["bottom"].split_row(
        Layout(name="agents"),
        Layout(name="system"),
    )

    layout["devops"].update(panels[1]())
    layout["revenue"].update(panels[2]())
    layout["agents"].update(panels[3]())
    layout["system"].update(panels[4]())

    layout["footer"].update(Panel(
        "[bold]q[/bold] Quit  [bold]r[/bold] Refresh  "
        "[bold]1-4[/bold] Focus panel  "
        "[dim]Auto-refresh active[/dim]",
        style="dim",
    ))

    return layout


def _key_listener(state: dict) -> None:
    """Background thread reading single keystrokes via tty raw mode."""
    try:
        import tty
        import termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while state["running"]:
                ch = sys.stdin.read(1)
                if ch in ("q", "Q", "\x03"):  # q or Ctrl+C
                    state["running"] = False
                elif ch == "r":
                    state["refresh"] = True
                elif ch in "01234":
                    state["focused"] = int(ch)
                    state["refresh"] = True
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except (ImportError, OSError):
        # Not a real terminal (e.g., piped input, Windows without tty)
        # Just wait until state["running"] is False
        while state["running"]:
            time.sleep(0.5)


def dash(
    refresh: int = typer.Option(30, "--refresh", "-r", help="Auto-refresh interval in seconds"),
    no_interactive: bool = typer.Option(False, "--no-interactive", help="Single render, no live mode"),
):
    """Launch interactive terminal dashboard."""
    if no_interactive:
        # Single render for testing or piped output
        console.print(_build_layout(0))
        return

    state = {"running": True, "refresh": False, "focused": 0}

    # Start keyboard listener in background thread
    listener = threading.Thread(target=_key_listener, args=(state,), daemon=True)
    listener.start()

    try:
        with Live(console=console, auto_refresh=False, screen=True) as live:
            while state["running"]:
                live.update(_build_layout(state["focused"]))
                live.refresh()

                # Sleep in small increments for responsive key handling
                for _ in range(refresh * 10):
                    if not state["running"] or state["refresh"]:
                        break
                    time.sleep(0.1)
                state["refresh"] = False
    except KeyboardInterrupt:
        pass
    finally:
        console.print("[dim]Dashboard closed.[/dim]")
