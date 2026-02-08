"""Recipe command group - workflow automation with step-based recipes."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List

import typer
from rich.table import Table

from src.core.console import console, success_panel, error_panel

recipe_app = typer.Typer(help="Workflow recipe management")


def _recipes_dir() -> Path:
    """Return the recipes directory, creating it if needed."""
    from src.core.config import get_config

    recipes_path = get_config().data_path / "recipes"
    recipes_path.mkdir(parents=True, exist_ok=True)
    return recipes_path


def _load_recipe(name: str) -> dict:
    """Load a recipe JSON file by name. Raises typer.Exit on failure."""
    path = _recipes_dir() / f"{name}.json"
    if not path.exists():
        error_panel("Recipe Not Found", f"No recipe named '{name}' at {path}")
        raise typer.Exit(code=1)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        error_panel("Recipe Error", f"Failed to read '{name}': {exc}")
        raise typer.Exit(code=1)
    return data


@recipe_app.command("list")
def list_recipes():
    """List available recipes."""
    recipes_path = _recipes_dir()
    files = sorted(recipes_path.glob("*.json"))

    if not files:
        console.print("[dim]No recipes found.[/dim] Create one with: mekon recipe create <name>")
        return

    table = Table(title="Available Recipes")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Steps", justify="right")

    for fp in files:
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            steps: List[dict] = data.get("steps", [])
            table.add_row(
                data.get("name", fp.stem),
                data.get("description", "-"),
                str(len(steps)),
            )
        except (json.JSONDecodeError, OSError):
            table.add_row(fp.stem, "[red]invalid json[/red]", "-")

    console.print(table)


@recipe_app.command()
def run(
    name: str = typer.Argument(..., help="Recipe name to execute"),
):
    """Execute a recipe by running its steps sequentially."""
    data = _load_recipe(name)
    steps: List[dict] = data.get("steps", [])

    if not steps:
        console.print("[yellow]Recipe has no steps.[/yellow]")
        return

    console.print(f"[bold]Running recipe:[/bold] {data.get('name', name)}")
    console.print(f"[dim]{data.get('description', '')}[/dim]\n")

    passed = 0
    failed = 0

    for idx, step in enumerate(steps, start=1):
        step_name = step.get("name", f"Step {idx}")
        command = step.get("command", "")
        continue_on_error = step.get("continue_on_error", False)

        with console.status(f"[bold green]Running step {idx}/{len(steps)}: {step_name}"):
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if result.returncode == 0:
                    console.print(f"  [green]PASS[/green] {step_name}")
                    passed += 1
                else:
                    console.print(f"  [red]FAIL[/red] {step_name}")
                    if result.stderr:
                        console.print(f"    [dim]{result.stderr.strip()[:200]}[/dim]")
                    failed += 1
                    if not continue_on_error:
                        console.print("[red]Stopping: continue_on_error is false.[/red]")
                        break
            except subprocess.TimeoutExpired:
                console.print(f"  [red]TIMEOUT[/red] {step_name}")
                failed += 1
                if not continue_on_error:
                    console.print("[red]Stopping: step timed out.[/red]")
                    break
            except OSError as exc:
                console.print(f"  [red]ERROR[/red] {step_name}: {exc}")
                failed += 1
                if not continue_on_error:
                    break

    # Summary
    console.print()
    if failed == 0:
        success_panel("Recipe Complete", f"All {passed} step(s) passed.")
    else:
        error_panel("Recipe Complete", f"{passed} passed, {failed} failed.")
        raise typer.Exit(code=1)


@recipe_app.command()
def create(
    name: str = typer.Argument(..., help="Name for the new recipe"),
):
    """Scaffold a new recipe template."""
    recipes_path = _recipes_dir()
    filepath = recipes_path / f"{name}.json"

    if filepath.exists():
        error_panel("Recipe Exists", f"Recipe '{name}' already exists at {filepath}")
        raise typer.Exit(code=1)

    template = {
        "name": name,
        "description": "Recipe description",
        "steps": [
            {"name": "Step 1", "command": "echo 'hello'", "continue_on_error": False},
        ],
    }

    filepath.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")
    success_panel("Recipe Created", f"Template saved to {filepath}")
