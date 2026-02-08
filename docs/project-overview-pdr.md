# Mekon CLI - Project Overview

## Purpose
All-in-one CLI companion for the Mekong ecosystem. Covers DevOps, Revenue, Marketing, and AI Agent management through a unified command interface.

## Architecture
Python CLI using Typer (commands) + Rich (terminal UI) + Pydantic (config). Bridges to mekong-cli's Plan-Execute-Verify engine for AI-powered task execution.

## Command Groups

| Group | Purpose | Key Commands |
|-------|---------|-------------|
| `devops` | Deploy, build, monitor | deploy, status, build, logs |
| `revenue` | Payment tracking, reports | dashboard, add, report, export |
| `marketing` | Leads, content, campaigns | hunt, content, campaign |
| `agents` | AI orchestration, LLM | list, run, cook, status |
| `system` | Config, health | config, health, info |

## Tech Stack
- **Language**: Python 3.9+
- **CLI**: Typer
- **Terminal UI**: Rich
- **Config**: Pydantic Settings + .env
- **Engine**: mekong-cli Plan-Execute-Verify (bridge)
- **Build**: Hatchling (PEP 517)

## Project Structure
```
mekon-cli/
├── src/
│   ├── main.py           # CLI entry point, registers all sub-apps
│   ├── core/
│   │   ├── config.py     # Pydantic settings from .env
│   │   ├── console.py    # Shared Rich console + formatting helpers
│   │   └── engine.py     # Bridge to mekong-cli Plan-Execute-Verify
│   ├── commands/
│   │   ├── devops.py     # DevOps: deploy, build, status, logs
│   │   ├── revenue.py    # Revenue: dashboard, add, report, export
│   │   ├── marketing.py  # Marketing: hunt, content, campaign
│   │   ├── agents.py     # Agents: list, run, cook, status
│   │   └── system.py     # System: config, health, info
│   └── utils/            # Shared utilities
├── tests/
│   └── test_cli.py       # CLI integration tests (11 tests)
├── pyproject.toml         # Project config + dependencies
└── .env.example           # Environment template
```

## Dependencies
- Runtime: typer, rich, pydantic, pydantic-settings, python-dotenv, requests, httpx
- Dev: pytest, pytest-asyncio, pytest-cov, ruff, mypy
- Optional: mekong-cli (for AI engine features)
