"""Data collectors for dashboard panels.

Each collector returns a Rich Panel renderable for display in the dashboard grid.
Collectors reuse logic from existing command modules where possible.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.core.config import get_config


def collect_devops() -> Panel:
    """Collect DevOps status: git branch, vercel, docker."""
    try:
        table = Table(show_header=True, header_style="bold", expand=True, box=None)
        table.add_column("Platform", style="cyan")
        table.add_column("Status")
        table.add_column("Info", style="dim")

        # Git
        try:
            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, timeout=3,
            )
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, timeout=3,
            )
            clean = not status.stdout.strip()
            table.add_row(
                "Git",
                "[green]clean[/green]" if clean else "[yellow]dirty[/yellow]",
                branch.stdout.strip(),
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            table.add_row("Git", "[dim]n/a[/dim]", "")

        # Vercel
        try:
            result = subprocess.run(
                ["vercel", "--version"],
                capture_output=True, text=True, timeout=3,
            )
            table.add_row("Vercel", "[green]installed[/green]", result.stdout.strip()[:20])
        except (FileNotFoundError, subprocess.TimeoutExpired):
            table.add_row("Vercel", "[dim]not found[/dim]", "")

        # Docker
        try:
            result = subprocess.run(
                ["docker", "info", "--format", "{{.ContainersRunning}}"],
                capture_output=True, text=True, timeout=3,
            )
            running = result.stdout.strip() if result.returncode == 0 else "?"
            table.add_row("Docker", "[green]running[/green]", f"{running} containers")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            table.add_row("Docker", "[dim]not found[/dim]", "")

        return Panel(table, title="[1] DevOps", border_style="blue")
    except Exception:
        return Panel("[dim]Unable to collect DevOps data[/dim]", title="[1] DevOps", border_style="red")


def collect_revenue() -> Panel:
    """Collect revenue summary from ledger."""
    try:
        config = get_config()
        ledger_file = config.data_path / "revenue" / "ledger.json"

        if not ledger_file.exists():
            return Panel(
                "[dim]No transactions yet[/dim]\n"
                "[dim]Use: mekon revenue add 100 --source client[/dim]",
                title="[2] Revenue",
                border_style="green",
            )

        entries = json.loads(ledger_file.read_text())
        total = sum(e.get("amount", 0) for e in entries)
        now = datetime.now()
        month_entries = [
            e for e in entries
            if e.get("date", "").startswith(now.strftime("%Y-%m"))
        ]
        month_total = sum(e.get("amount", 0) for e in month_entries)

        # Last 3 transactions
        recent_lines = []
        for e in entries[-3:]:
            amt = e.get("amount", 0)
            src = e.get("source", "?")
            recent_lines.append(f"  ${amt:,.0f} from {src}")

        content = (
            f"[bold]Total:[/bold]  ${total:,.2f}\n"
            f"[bold]Month:[/bold]  ${month_total:,.2f}\n"
            f"[bold]Txns:[/bold]   {len(entries)}\n"
        )
        if recent_lines:
            content += "\n[dim]Recent:[/dim]\n" + "\n".join(recent_lines)

        return Panel(content, title="[2] Revenue", border_style="green")
    except Exception:
        return Panel("[dim]Unable to load revenue data[/dim]", title="[2] Revenue", border_style="red")


def collect_agents() -> Panel:
    """Collect agent system health."""
    try:
        config = get_config()

        lines = []

        # Mekong engine
        mekong_ok = config.mekong_path.exists()
        status = "[green]available[/green]" if mekong_ok else "[red]missing[/red]"
        lines.append(f"[bold]Engine:[/bold]   {status}")

        # LLM API
        has_key = bool(config.llm_api_key)
        status = "[green]configured[/green]" if has_key else "[yellow]no key[/yellow]"
        lines.append(f"[bold]LLM API:[/bold]  {status}")
        lines.append(f"[bold]Model:[/bold]    {config.llm_model}")

        # Data dir
        data_ok = config.data_path.exists()
        status = "[green]exists[/green]" if data_ok else "[dim]not created[/dim]"
        lines.append(f"[bold]Data:[/bold]     {status}")

        return Panel("\n".join(lines), title="[3] Agents", border_style="magenta")
    except Exception:
        return Panel("[dim]Unable to check agents[/dim]", title="[3] Agents", border_style="red")


def collect_system() -> Panel:
    """Collect system tool versions."""
    try:
        table = Table(show_header=True, header_style="bold", expand=True, box=None)
        table.add_column("Tool", style="cyan")
        table.add_column("Status")
        table.add_column("Version", style="dim")

        checks = [
            ("Python", "python3 --version"),
            ("Git", "git --version"),
            ("Node", "node --version"),
        ]

        for name, cmd in checks:
            try:
                result = subprocess.run(
                    cmd.split(),
                    capture_output=True, text=True, timeout=3,
                )
                if result.returncode == 0:
                    ver = result.stdout.strip().split("\n")[0]
                    table.add_row(name, "[green]OK[/green]", ver[:25])
                else:
                    table.add_row(name, "[yellow]err[/yellow]", "")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                table.add_row(name, "[dim]n/a[/dim]", "")

        return Panel(table, title="[4] System", border_style="cyan")
    except Exception:
        return Panel("[dim]Unable to check system[/dim]", title="[4] System", border_style="red")
