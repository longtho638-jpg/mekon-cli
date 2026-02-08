# Mekon CLI

All-in-one CLI for the Mekong ecosystem.

[![CI](https://github.com/longtho638-jpg/mekon-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/longtho638-jpg/mekon-cli/actions/workflows/ci.yml)

## Features

- **DevOps** -- Deploy, build, and monitor infrastructure
- **Revenue** -- Track payments, dashboards, and financial reports
- **Marketing** -- Hunt leads, create content, run campaigns
- **AI Agents** -- Orchestrate agents and manage LLM workflows
- **System** -- Configuration, health checks, system info
- **Market Research** -- Domain research, page analysis, competitor tracking
- **Logs** -- Activity log viewer and management
- **Recipes** -- Workflow automation with reusable recipes
- **Dashboard** -- Interactive terminal dashboard
- **Init** -- Project initialization wizard

## Install

```bash
git clone https://github.com/longtho638-jpg/mekon-cli.git
cd mekon-cli
pip install -e ".[dev]"
```

## Quick Start

```bash
mekon --help                          # Show all commands
mekon devops deploy vercel            # Deploy to Vercel
mekon revenue dashboard              # Open revenue dashboard
mekon marketing hunt example.com     # Hunt leads from a domain
mekon agents cook "deploy auth"      # Run an AI agent task
mekon system health                  # Check system health
mekon market research example.com    # Research a market domain
mekon logs show                      # View activity logs
mekon recipe list                    # List available recipes
mekon dash                           # Launch terminal dashboard
mekon init                           # Initialize a new project
```

## Command Reference

| Group | Subcommands | Description |
|-------|-------------|-------------|
| `mekon devops` | `deploy`, `status`, `build`, `logs` | Infrastructure deployment and monitoring |
| `mekon revenue` | `dashboard`, `add`, `report`, `export` | Payment tracking and financial analytics |
| `mekon marketing` | `hunt`, `content`, `campaign` | Lead generation, content, and campaigns |
| `mekon agents` | `list`, `run`, `cook`, `status` | AI agent orchestration and LLM management |
| `mekon system` | `config`, `health`, `info` | System configuration and diagnostics |
| `mekon market` | `research`, `analyze`, `competitors` | Market research and competitor analysis |
| `mekon logs` | `show`, `tail`, `clear` | Activity log viewer and management |
| `mekon recipe` | `list`, `run`, `create` | Workflow recipe automation |

**Standalone commands:**

| Command | Description |
|---------|-------------|
| `mekon dash` | Interactive terminal dashboard |
| `mekon init` | Initialize a new project |
| `mekon version` | Show version info |

## Architecture

Mekon CLI is built on:

- **[Typer](https://typer.tiangolo.com/)** -- CLI framework with auto-generated help
- **[Rich](https://rich.readthedocs.io/)** -- Terminal formatting, tables, panels
- **[Pydantic](https://docs.pydantic.dev/)** -- Settings and data validation
- **mekong-cli bridge** -- Plan-Execute-Verify engine for operations

The CLI is organized into domain-specific command groups registered as Typer sub-apps, with standalone commands for the dashboard and project init.

## Development

```bash
# Clone and install
git clone https://github.com/longtho638-jpg/mekon-cli.git
cd mekon-cli
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Lint
ruff check src/ tests/

# Type check
mypy src/ --ignore-missing-imports
```

### Project Structure

```
src/
  main.py              # App entry point, command registration
  commands/            # Domain command groups (devops, revenue, etc.)
  core/                # Shared core modules (console, config, bridge)
  utils/               # Utility helpers
tests/
  test_cli.py          # CLI tests
```

## License

MIT
