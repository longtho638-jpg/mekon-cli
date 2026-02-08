"""Mekon CLI - All-in-one CLI for the Mekong ecosystem.

Covers: DevOps, Revenue, Marketing, AI Agents.
Powered by mekong-cli's Plan-Execute-Verify engine.
"""

import typer
from rich.panel import Panel
from rich.text import Text

from src.core.console import console
from src.commands.devops import devops_app
from src.commands.revenue import revenue_app
from src.commands.marketing import marketing_app
from src.commands.agents import agents_app
from src.commands.system import system_app
from src.commands.dashboard import dash

app = typer.Typer(
    name="mekon",
    help="Mekon CLI: All-in-one toolkit for the Mekong ecosystem",
    add_completion=False,
)

# Register domain sub-apps
app.add_typer(devops_app, name="devops", help="DevOps: deploy, build, monitor")
app.add_typer(revenue_app, name="revenue", help="Revenue: payments, analytics, reports")
app.add_typer(marketing_app, name="marketing", help="Marketing: leads, content, campaigns")
app.add_typer(agents_app, name="agents", help="Agents: AI orchestration, LLM management")
app.add_typer(system_app, name="system", help="System: config, health, info")

# Register standalone commands
app.command(name="dash")(dash)


@app.command()
def version():
    """Show version info."""
    from src import __version__

    console.print(Panel(
        f"[bold green]Mekon CLI[/bold green] v{__version__}\n"
        "[dim]All-in-one CLI for the Mekong ecosystem[/dim]",
        title="Version",
        border_style="blue",
    ))


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Mekon CLI: All-in-one toolkit for the Mekong ecosystem."""
    if ctx.invoked_subcommand is None:
        console.print(Panel(
            Text("Mekon CLI", style="bold green"),
            subtitle="All-in-one toolkit for the Mekong ecosystem",
            border_style="green",
        ))
        console.print(
            "\n[bold]Command Groups:[/bold]\n"
            "  [cyan]devops[/cyan]      Deploy, build, monitor infrastructure\n"
            "  [cyan]revenue[/cyan]     Track payments, generate reports\n"
            "  [cyan]marketing[/cyan]   Hunt leads, create content, run campaigns\n"
            "  [cyan]agents[/cyan]      AI agent orchestration and LLM management\n"
            "  [cyan]system[/cyan]      Configuration, health checks, info\n"
            "\n[dim]Run[/dim] [bold cyan]mekon --help[/bold cyan] [dim]for all options[/dim]"
        )


if __name__ == "__main__":
    app()
