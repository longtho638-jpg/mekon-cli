"""Agents command group - AI agent management, orchestration, LLM control."""

import subprocess
from pathlib import Path

import typer
from rich.table import Table
from rich.panel import Panel

from src.core.console import console, info_panel, error_panel, success_panel
from src.core.config import get_config
from src.core.engine import run_goal, plan_goal

agents_app = typer.Typer(help="Agents: AI agent orchestration, LLM management")


@agents_app.command(name="list")
def list_agents():
    """List available agents from mekong-cli."""
    config = get_config()
    mekong_path = config.mekong_path
    agents_dir = mekong_path / "src" / "agents"

    if not agents_dir.exists():
        error_panel("Agents", f"Agents directory not found: {agents_dir}")
        console.print("[dim]Ensure MEKONG_CLI_PATH is set correctly in .env[/dim]")
        return

    table = Table(title="Available Agents")
    table.add_column("Agent", style="cyan")
    table.add_column("File", style="dim")
    table.add_column("Size", justify="right")

    for py_file in sorted(agents_dir.glob("*.py")):
        if py_file.name.startswith("__"):
            continue
        name = py_file.stem.replace("_", " ").title()
        size = py_file.stat().st_size
        table.add_row(name, py_file.name, f"{size:,} B")

    console.print(table)


@agents_app.command()
def run(
    agent: str = typer.Argument(..., help="Agent name (e.g., git, file, lead-hunter)"),
    command: str = typer.Argument(..., help="Command to run on the agent"),
):
    """Run a specific agent with a command."""
    goal = f"Use {agent} agent to {command}"
    info_panel("Agent Run", f"Agent: {agent} | Command: {command}")

    result = run_goal(goal, strict=False)
    status = result.get("status", "unknown")

    if status == "success":
        success_panel("Agent Result", f"Completed: {result.get('completed_steps', 0)} steps")
    elif status == "error":
        error_panel("Agent Error", result.get("message", "Failed"))
    else:
        console.print(f"[yellow]Status: {status}[/yellow]")
        for err in result.get("errors", []):
            console.print(f"  [red]{err}[/red]")


@agents_app.command()
def cook(
    goal: str = typer.Argument(..., help="Goal to plan-execute-verify"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Plan only, no execution"),
):
    """Run the Plan-Execute-Verify pipeline for a goal."""
    if dry_run:
        info_panel("Plan Mode", f"Goal: {goal}")
        result = plan_goal(goal)

        if result.get("status") == "error":
            error_panel("Plan Error", result.get("message", "Engine not available"))
            return

        console.print(Panel(
            f"[bold]{result.get('name', '')}[/bold]\n{result.get('description', '')}",
            title="Generated Plan",
            border_style="cyan",
        ))

        steps = result.get("steps", [])
        if steps:
            table = Table(title="Steps (dry run - not executed)")
            table.add_column("#", style="bold cyan", justify="right")
            table.add_column("Task", style="bold")
            table.add_column("Description", style="dim")
            for step in steps:
                table.add_row(str(step["order"]), step["title"], step["description"][:70])
            console.print(table)
    else:
        info_panel("Cook", f"Goal: {goal}")
        result = run_goal(goal)
        status = result.get("status", "unknown")

        if status == "success":
            success_panel("Mission Complete", f"Steps: {result.get('completed_steps', 0)}/{result.get('total_steps', 0)}")
        else:
            error_panel("Mission Failed", f"Status: {status}")
            for err in result.get("errors", []):
                console.print(f"  [red]{err}[/red]")
            raise typer.Exit(code=1)


@agents_app.command()
def status():
    """Show agent system health and LLM status."""
    config = get_config()

    table = Table(title="Agent System Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status")
    table.add_column("Details", style="dim")

    # Check mekong-cli
    mekong_exists = config.mekong_path.exists()
    table.add_row(
        "Mekong Engine",
        "[green]available[/green]" if mekong_exists else "[red]missing[/red]",
        str(config.mekong_path),
    )

    # Check LLM config
    has_key = bool(config.llm_api_key)
    table.add_row(
        "LLM API",
        "[green]configured[/green]" if has_key else "[yellow]no key[/yellow]",
        f"Model: {config.llm_model}",
    )

    # Check data dir
    data_exists = config.data_path.exists()
    table.add_row(
        "Data Directory",
        "[green]exists[/green]" if data_exists else "[dim]not created[/dim]",
        str(config.data_path),
    )

    console.print(table)
