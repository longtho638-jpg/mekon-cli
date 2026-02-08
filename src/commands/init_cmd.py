"""Project initialization command for Mekon CLI.

Creates .env, data directories, detects mekong-cli, and runs health checks.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import typer

from src.core.config import get_config
from src.core.console import console, success_panel, error_panel, info_panel


_DATA_SUBDIRS = ("revenue", "logs", "recipes")
_ENV_EXAMPLE = Path(".env.example")
_ENV_FILE = Path(".env")


def _copy_env_template() -> str:
    """Copy .env.example to .env if .env does not exist. Return status message."""
    if _ENV_FILE.exists():
        return "[dim]already exists[/dim]"
    if not _ENV_EXAMPLE.exists():
        return "[yellow]template .env.example not found[/yellow]"
    shutil.copy2(_ENV_EXAMPLE, _ENV_FILE)
    return "[green]created from .env.example[/green]"


def _create_data_dirs(base: Path) -> list[str]:
    """Create ~/.mekon and subdirectories. Return list of status lines."""
    lines: list[str] = []
    base.mkdir(parents=True, exist_ok=True)
    lines.append(f"  {base} [green]ready[/green]")
    for sub in _DATA_SUBDIRS:
        p = base / sub
        p.mkdir(parents=True, exist_ok=True)
        lines.append(f"  {p} [green]ready[/green]")
    return lines


def _detect_mekong_cli() -> tuple[str, str]:
    """Auto-detect mekong-cli path. Return (path, status)."""
    import os

    # Priority: env var > config > ../mekong-cli > ~/mekong-cli
    env_val = os.environ.get("MEKONG_CLI_PATH", "")
    if env_val:
        p = Path(env_val).expanduser().resolve()
        if p.exists():
            return str(p), "[green]found (env)[/green]"

    cfg = get_config()
    if cfg.mekong_path.exists():
        return str(cfg.mekong_path), "[green]found (config)[/green]"

    candidates = [
        Path("../mekong-cli").resolve(),
        Path.home() / "mekong-cli",
    ]
    for c in candidates:
        if c.exists():
            return str(c), "[green]found[/green]"

    return "", "[yellow]not found[/yellow]"


def _run_health_check() -> list[str]:
    """Quick health check: Python version and key pip packages. Return status lines."""
    lines: list[str] = []
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    lines.append(f"  Python {py_ver} [green]OK[/green]")

    for pkg in ("typer", "rich", "pydantic"):
        try:
            result = subprocess.run(
                [sys.executable, "-c", f"import {pkg}; print({pkg}.__version__)"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                ver = result.stdout.strip()
                lines.append(f"  {pkg} {ver} [green]OK[/green]")
            else:
                lines.append(f"  {pkg} [red]import error[/red]")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            lines.append(f"  {pkg} [red]check failed[/red]")
    return lines


def init_cmd() -> None:
    """Initialize a new Mekon project: .env, data dirs, mekong-cli detection."""
    console.print("[bold cyan]Initializing Mekon project...[/bold cyan]\n")

    # 1. .env setup
    env_status = _copy_env_template()
    console.print(f"[bold].env[/bold]: {env_status}")

    # 2. Data directories
    cfg = get_config()
    dir_lines = _create_data_dirs(cfg.data_path)
    console.print("\n[bold]Data directories:[/bold]")
    for line in dir_lines:
        console.print(line)

    # 3. Mekong-cli detection
    mekong_path, mekong_status = _detect_mekong_cli()
    console.print(f"\n[bold]Mekong CLI:[/bold] {mekong_status}")
    if mekong_path:
        console.print(f"  [dim]{mekong_path}[/dim]")

    # 4. Health check
    console.print("\n[bold]Health check:[/bold]")
    for line in _run_health_check():
        console.print(line)

    # 5. Summary panel
    console.print()
    success_panel("Init Complete", "Mekon project initialized successfully. Run 'mekon system health' for full checks.")
