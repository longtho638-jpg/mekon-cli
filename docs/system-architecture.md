# System Architecture

## Overview
```
┌─────────────────────────────────────────────┐
│              mekon CLI (Typer)               │
├──────┬──────┬──────┬──────┬────────────────┤
│devops│revenue│market│agents│    system      │
│  app │  app │  app │ app  │     app        │
└──┬───┴──┬───┴──┬───┴──┬───┴────┬───────────┘
   │      │      │      │        │
   └──────┴──────┴──────┴────────┘
                 │
   ┌─────────────┴─────────────┐
   │     src/core/ (shared)    │
   ├───────────────────────────┤
   │ console.py  - Rich output │
   │ config.py   - Pydantic    │
   │ engine.py   - PEV bridge  │
   └─────────────┬─────────────┘
                 │ (optional)
   ┌─────────────┴─────────────┐
   │   mekong-cli (sibling)    │
   │   Plan-Execute-Verify     │
   │   LLM Client              │
   │   Agents (Git, File, etc) │
   └───────────────────────────┘
```

## Data Flow
1. User invokes `mekon <group> <command> [args]`
2. Typer routes to the right sub-app command function
3. Command reads config from `.env` via Pydantic Settings
4. For AI tasks: engine.py bridges to mekong-cli's orchestrator
5. For direct ops: subprocess calls to platform CLIs (vercel, docker, etc)
6. Rich console renders results with panels/tables

## Config Resolution
```
.env → MekonConfig (Pydantic Settings) → command functions
```

## Engine Bridge
The engine module (`src/core/engine.py`) does lazy import of mekong-cli:
1. Reads `MEKONG_CLI_PATH` from config
2. Adds mekong-cli root to `sys.path` at runtime
3. Imports `RecipeOrchestrator` and `RecipePlanner`
4. Falls back gracefully if mekong-cli not available

## Data Storage
- Revenue ledger: `~/.mekon/revenue/ledger.json`
- Config: `.env` in project root
- Logs: subprocess stdout/stderr (not persisted)
