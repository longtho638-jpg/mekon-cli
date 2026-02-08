"""System command group - config, health, version info."""

import typer
from rich.panel import Panel
from rich.table import Table

from src.core.console import console
from src.core.config import get_config

system_app = typer.Typer(help="System: configuration, health checks, info")


@system_app.command()
def config():
    """Show current configuration."""
    cfg = get_config()

    table = Table(title="Mekon Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value")

    table.add_row("LLM API URL", cfg.llm_api_url)
    table.add_row("LLM Model", cfg.llm_model)
    table.add_row("LLM API Key", "***" + cfg.llm_api_key[-4:] if cfg.llm_api_key else "[red]not set[/red]")
    table.add_row("Mekong CLI Path", str(cfg.mekong_path))
    table.add_row("Data Directory", str(cfg.data_path))
    table.add_row("Vercel Token", "set" if cfg.vercel_token else "[dim]not set[/dim]")
    table.add_row("Cloudflare Token", "set" if cfg.cloudflare_token else "[dim]not set[/dim]")

    console.print(table)


@system_app.command()
def health():
    """Run system health checks."""
    import subprocess

    cfg = get_config()

    checks = [
        ("Python", "python3 --version"),
        ("Git", "git --version"),
        ("Node", "node --version"),
        ("Vercel", "vercel --version"),
        ("Docker", "docker --version"),
    ]

    table = Table(title="System Health")
    table.add_column("Tool", style="cyan")
    table.add_column("Status")
    table.add_column("Version", style="dim")

    for name, cmd in checks:
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                version = result.stdout.strip().split("\n")[0]
                table.add_row(name, "[green]OK[/green]", version)
            else:
                table.add_row(name, "[yellow]error[/yellow]", "")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            table.add_row(name, "[dim]not found[/dim]", "")

    # Check mekong-cli
    mekong_ok = cfg.mekong_path.exists()
    table.add_row(
        "Mekong CLI",
        "[green]found[/green]" if mekong_ok else "[red]missing[/red]",
        str(cfg.mekong_path) if mekong_ok else "",
    )

    console.print(table)


@system_app.command()
def info():
    """Show mekon-cli version and system info."""
    from src import __version__

    console.print(Panel(
        f"[bold green]Mekon CLI[/bold green] v{__version__}\n"
        "[dim]All-in-one CLI for the Mekong ecosystem[/dim]\n\n"
        "[bold]Domains:[/bold]\n"
        "  devops     - Deploy, build, monitor\n"
        "  revenue    - Track payments, reports\n"
        "  marketing  - Leads, content, campaigns\n"
        "  agents     - AI orchestration, LLM mgmt\n"
        "  system     - Config, health, info",
        title="About",
        border_style="blue",
    ))
