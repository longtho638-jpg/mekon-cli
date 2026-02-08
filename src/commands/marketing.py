"""Marketing command group - lead hunting, content generation, campaigns."""

import typer
from rich.table import Table
from rich.panel import Panel

from src.core.console import console, info_panel, error_panel
from src.core.engine import run_goal, plan_goal

marketing_app = typer.Typer(help="Marketing: leads, content, campaigns")


@marketing_app.command()
def hunt(
    domain: str = typer.Argument(..., help="Domain to hunt leads from"),
    depth: str = typer.Option("shallow", "--depth", "-d", help="Search depth: shallow, deep"),
):
    """Hunt for leads and decision-makers at a company."""
    info_panel("Lead Hunter", f"Hunting leads at: {domain}")

    goal = f"Find CEO and key decision makers at {domain}, including emails and LinkedIn profiles"
    if depth == "deep":
        goal += ". Do a deep search across LinkedIn, Crunchbase, and company website."

    result = plan_goal(goal)

    if result.get("status") == "error":
        error_panel("Hunt Error", result.get("message", "Engine not available"))
        console.print("[dim]Tip: Ensure MEKONG_CLI_PATH points to mekong-cli[/dim]")
        return

    console.print(Panel(
        f"[bold]{result.get('name', 'Lead Hunt Plan')}[/bold]\n{result.get('description', '')}",
        title="Lead Hunt Plan",
        border_style="cyan",
    ))

    steps = result.get("steps", [])
    if steps:
        table = Table(title="Hunt Steps")
        table.add_column("#", style="bold cyan", justify="right")
        table.add_column("Step", style="bold")
        table.add_column("Details", style="dim")

        for step in steps:
            table.add_row(str(step["order"]), step["title"], step["description"][:60])
        console.print(table)


@marketing_app.command()
def content(
    topic: str = typer.Argument(..., help="Content topic or keyword"),
    content_type: str = typer.Option("article", "--type", "-t", help="Type: article, social, email"),
    execute: bool = typer.Option(False, "--execute", help="Execute the content plan"),
):
    """Generate content plan for a topic."""
    type_label = {"article": "SEO article", "social": "social media posts", "email": "email campaign"}
    label = type_label.get(content_type, content_type)

    goal = f"Create {label} about: {topic}"

    if execute:
        info_panel("Content Writer", f"Generating {label}: {topic}")
        result = run_goal(goal)
        status = result.get("status", "unknown")
        if status == "success":
            console.print(f"[green]Content generated: {result.get('completed_steps', 0)} steps done[/green]")
        else:
            error_panel("Content Error", f"Status: {status}")
            for err in result.get("errors", []):
                console.print(f"  [red]{err}[/red]")
    else:
        result = plan_goal(goal)
        if result.get("status") == "error":
            error_panel("Content Error", result.get("message", "Engine not available"))
            return

        console.print(Panel(
            f"[bold]{result.get('name', '')}[/bold]\n{result.get('description', '')}",
            title=f"Content Plan: {label}",
            border_style="cyan",
        ))

        steps = result.get("steps", [])
        if steps:
            table = Table(title="Steps")
            table.add_column("#", style="bold cyan", justify="right")
            table.add_column("Step", style="bold")
            for step in steps:
                table.add_row(str(step["order"]), step["title"])

            console.print(table)
            console.print(f"\n[dim]Add --execute to run this plan[/dim]")


@marketing_app.command()
def campaign(
    name: str = typer.Argument(..., help="Campaign name or goal"),
    channels: str = typer.Option("all", "--channels", "-c", help="Channels: email, social, ads, all"),
):
    """Plan a marketing campaign across channels."""
    channel_list = channels if channels != "all" else "email, social media, and paid ads"
    goal = f"Plan marketing campaign '{name}' across {channel_list}"

    result = plan_goal(goal)

    if result.get("status") == "error":
        error_panel("Campaign Error", result.get("message", "Engine not available"))
        return

    console.print(Panel(
        f"[bold]{result.get('name', '')}[/bold]\n{result.get('description', '')}",
        title=f"Campaign: {name}",
        border_style="magenta",
    ))

    steps = result.get("steps", [])
    if steps:
        table = Table(title="Campaign Steps")
        table.add_column("#", style="bold cyan", justify="right")
        table.add_column("Action", style="bold")
        table.add_column("Description", style="dim")
        for step in steps:
            table.add_row(str(step["order"]), step["title"], step["description"][:60])
        console.print(table)
