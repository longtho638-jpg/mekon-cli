"""Mekong CLI engine bridge - connects to mekong-cli's Plan-Execute-Verify core."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from src.core.config import get_config
from src.core.console import console, error_panel


def _ensure_mekong_importable() -> bool:
    """Add mekong-cli to sys.path if available."""
    config = get_config()
    mekong_path = config.mekong_path

    if not mekong_path.exists():
        return False

    mekong_str = str(mekong_path)
    if mekong_str not in sys.path:
        sys.path.insert(0, mekong_str)
    return True


def get_orchestrator(strict: bool = True, rollback: bool = True) -> Any:
    """Get a RecipeOrchestrator from mekong-cli if available."""
    if not _ensure_mekong_importable():
        error_panel("Engine Error", "mekong-cli not found. Set MEKONG_CLI_PATH in .env")
        return None

    try:
        from src.core.orchestrator import RecipeOrchestrator
        from src.core.llm_client import get_client

        llm = get_client()
        return RecipeOrchestrator(
            llm_client=llm if llm.is_available else None,
            strict_verification=strict,
            enable_rollback=rollback,
        )
    except ImportError as e:
        error_panel("Import Error", f"Cannot import mekong-cli engine: {e}")
        return None


def get_planner() -> Any:
    """Get a RecipePlanner from mekong-cli if available."""
    if not _ensure_mekong_importable():
        return None

    try:
        from src.core.planner import RecipePlanner
        from src.core.llm_client import get_client

        llm = get_client()
        return RecipePlanner(llm_client=llm if llm.is_available else None)
    except ImportError:
        return None


def run_goal(goal: str, strict: bool = True) -> dict[str, Any]:
    """Execute a goal through mekong-cli's Plan-Execute-Verify engine."""
    orchestrator = get_orchestrator(strict=strict)
    if not orchestrator:
        return {"status": "error", "message": "Engine not available"}

    result = orchestrator.run_from_goal(goal)
    return {
        "status": result.status.value,
        "total_steps": result.total_steps,
        "completed_steps": result.completed_steps,
        "success_rate": result.success_rate,
        "errors": result.errors,
    }


def plan_goal(goal: str) -> dict[str, Any]:
    """Plan a goal without execution."""
    planner = get_planner()
    if not planner:
        return {"status": "error", "message": "Planner not available"}

    recipe = planner.plan(goal)
    return {
        "name": recipe.name,
        "description": recipe.description,
        "steps": [
            {"order": s.order, "title": s.title, "description": s.description}
            for s in recipe.steps
        ],
    }
