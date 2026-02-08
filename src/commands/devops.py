"""DevOps command group - deployment, infrastructure, monitoring."""

from __future__ import annotations

import subprocess
from pathlib import Path

import typer
from rich.table import Table

from src.core.console import console, success_panel, error_panel, info_panel

devops_app = typer.Typer(help="DevOps: deploy, monitor, manage infrastructure")


@devops_app.command()
def deploy(
    target: str = typer.Argument(..., help="Deploy target: vercel, cloudflare, docker"),
    project: str = typer.Option(".", "--project", "-p", help="Project directory"),
    prod: bool = typer.Option(False, "--prod", help="Deploy to production"),
):
    """Deploy a project to target platform."""
    project_path = Path(project).resolve()

    if not project_path.exists():
        error_panel("Deploy Error", f"Project not found: {project_path}")
        raise typer.Exit(code=1)

    deployers = {
        "vercel": _deploy_vercel,
        "cloudflare": _deploy_cloudflare,
        "docker": _deploy_docker,
    }

    deployer = deployers.get(target)
    if not deployer:
        error_panel("Deploy Error", f"Unknown target: {target}. Use: {', '.join(deployers)}")
        raise typer.Exit(code=1)

    deployer(project_path, prod)


@devops_app.command()
def status(
    project: str = typer.Option(".", "--project", "-p", help="Project directory"),
):
    """Check deployment status across platforms."""
    project_path = Path(project).resolve()

    table = Table(title="Deployment Status")
    table.add_column("Platform", style="cyan")
    table.add_column("Status")
    table.add_column("URL", style="dim")

    # Check Vercel
    vercel_status = _check_vercel(project_path)
    table.add_row("Vercel", vercel_status["status"], vercel_status.get("url", "-"))

    # Check git status
    git_status = _check_git(project_path)
    table.add_row("Git", git_status["status"], git_status.get("branch", "-"))

    console.print(table)


@devops_app.command()
def logs(
    target: str = typer.Argument("vercel", help="Platform to fetch logs from"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of log lines"),
):
    """Fetch deployment logs."""
    try:
        if target == "vercel":
            result = subprocess.run(
                ["vercel", "logs", "--limit", str(lines)],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                console.print(result.stdout)
            else:
                error_panel("Logs Error", result.stderr or "Failed to fetch logs")
        else:
            error_panel("Logs Error", f"Unsupported platform: {target}")
    except FileNotFoundError:
        error_panel("Logs Error", f"{target} CLI not installed")
    except subprocess.TimeoutExpired:
        error_panel("Logs Error", "Timed out fetching logs")


@devops_app.command()
def build(
    project: str = typer.Option(".", "--project", "-p", help="Project directory"),
    cmd: str = typer.Option("npm run build", "--cmd", "-c", help="Build command"),
):
    """Run build command and report results."""
    project_path = Path(project).resolve()

    with console.status("[bold green]Building..."):
        try:
            result = subprocess.run(
                cmd.split(),
                cwd=project_path,
                capture_output=True, text=True, timeout=300,
            )
            if result.returncode == 0:
                success_panel("Build", "Build completed successfully")
                if result.stdout:
                    console.print(f"[dim]{result.stdout[-500:]}[/dim]")
            else:
                error_panel("Build Failed", result.stderr[-500:] if result.stderr else "Unknown error")
                raise typer.Exit(code=1)
        except FileNotFoundError:
            error_panel("Build Error", f"Command not found: {cmd.split()[0]}")
            raise typer.Exit(code=1)
        except subprocess.TimeoutExpired:
            error_panel("Build Error", "Build timed out (5m limit)")
            raise typer.Exit(code=1)


def _deploy_vercel(project_path: Path, prod: bool) -> None:
    """Deploy to Vercel."""
    cmd = ["vercel"]
    if prod:
        cmd.append("--prod")

    with console.status("[bold green]Deploying to Vercel..."):
        try:
            result = subprocess.run(
                cmd, cwd=project_path,
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                url = result.stdout.strip().split("\n")[-1]
                success_panel("Vercel Deploy", f"Deployed: {url}")
            else:
                error_panel("Vercel Error", result.stderr or "Deploy failed")
                raise typer.Exit(code=1)
        except FileNotFoundError:
            error_panel("Vercel Error", "vercel CLI not installed. Run: npm i -g vercel")
            raise typer.Exit(code=1)


def _deploy_cloudflare(project_path: Path, prod: bool) -> None:
    """Deploy to Cloudflare Workers."""
    cmd = ["wrangler", "deploy"]
    if not prod:
        cmd.append("--dry-run")

    with console.status("[bold green]Deploying to Cloudflare..."):
        try:
            result = subprocess.run(
                cmd, cwd=project_path,
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                success_panel("Cloudflare Deploy", result.stdout[-200:] if result.stdout else "OK")
            else:
                error_panel("Cloudflare Error", result.stderr or "Deploy failed")
                raise typer.Exit(code=1)
        except FileNotFoundError:
            error_panel("Cloudflare Error", "wrangler CLI not installed. Run: npm i -g wrangler")
            raise typer.Exit(code=1)


def _deploy_docker(project_path: Path, prod: bool) -> None:
    """Build and optionally push Docker image."""
    tag = "latest" if prod else "dev"

    with console.status("[bold green]Building Docker image..."):
        try:
            result = subprocess.run(
                ["docker", "build", "-t", f"mekon-app:{tag}", "."],
                cwd=project_path,
                capture_output=True, text=True, timeout=300,
            )
            if result.returncode == 0:
                success_panel("Docker Build", f"Image built: mekon-app:{tag}")
            else:
                error_panel("Docker Error", result.stderr[-300:] if result.stderr else "Build failed")
                raise typer.Exit(code=1)
        except FileNotFoundError:
            error_panel("Docker Error", "docker not installed")
            raise typer.Exit(code=1)


def _check_vercel(project_path: Path) -> dict[str, str]:
    """Check Vercel deployment status."""
    try:
        result = subprocess.run(
            ["vercel", "ls", "--json"],
            cwd=project_path,
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            return {"status": "[green]active[/green]", "url": "See vercel dashboard"}
        return {"status": "[yellow]unknown[/yellow]"}
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {"status": "[dim]not configured[/dim]"}


def _check_git(project_path: Path) -> dict[str, str]:
    """Check git status."""
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_path,
            capture_output=True, text=True, timeout=5,
        )
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_path,
            capture_output=True, text=True, timeout=5,
        )
        clean = len(status.stdout.strip().split("\n")) == 1 and not status.stdout.strip()
        return {
            "status": "[green]clean[/green]" if clean else "[yellow]dirty[/yellow]",
            "branch": branch.stdout.strip(),
        }
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {"status": "[dim]not a git repo[/dim]"}
