---
title: "Interactive Terminal Dashboard"
description: "Rich Layout+Live TUI dashboard via `mekon dash` showing all domain panels"
status: pending
priority: P2
effort: 3h
branch: feat/terminal-dashboard
tags: [tui, dashboard, rich]
created: 2026-02-09
---

# Terminal Dashboard Plan

## Files to Modify/Create

| File | Action | Purpose |
|------|--------|---------|
| `src/commands/dashboard.py` | CREATE | Dashboard command + rendering logic |
| `src/core/collectors.py` | CREATE | Data collectors for each domain panel |
| `src/main.py` | MODIFY | Register `dash` command (2 lines) |

## Layout Design (4-panel grid)

```
+---------------------------+---------------------------+
|  [1] DevOps Status        |  [2] Revenue Summary      |
|  Platform  Status   URL   |  Total: $X   Month: $Y   |
|  Vercel    active   ...   |  Txns: N     Sources: N   |
|  Git       clean    main  |  Last 3 transactions...   |
+---------------------------+---------------------------+
|  [3] Agent Health         |  [4] System Health        |
|  Engine    available      |  Python   OK   3.12       |
|  LLM API   configured    |  Git      OK   2.43       |
|  Data Dir  exists         |  Node     OK   20.x      |
+---------------------------+---------------------------+
|  [q] Quit  [r] Refresh  [1-4] Focus panel  Auto: 30s |
+-----------------------------------------------------------+
```

Uses `Rich.Layout` with 2 rows x 2 cols + footer row.

## Key Bindings

| Key | Action |
|-----|--------|
| `q` / `Ctrl+C` | Quit dashboard |
| `r` | Force refresh |
| `1-4` | Toggle expanded view for domain panel |
| `0` | Return to grid view |

## Data Collectors (`src/core/collectors.py`)

Each returns a `Rich.Table` or `Rich.Panel` renderable. Reuses existing logic:

1. **DevOps** - calls `_check_vercel()`, `_check_git()` from `devops.py`
2. **Revenue** - reads `~/.mekon/revenue/ledger.json`, computes totals
3. **Agents** - checks `config.mekong_path.exists()`, `config.llm_api_key`
4. **System** - runs `subprocess` version checks (Python, Git, Node, etc.)

All collectors wrapped in `try/except` returning fallback "unavailable" panels.

## Implementation Steps

### Step 1: Create `src/core/collectors.py` (~80 lines)

```python
def collect_devops() -> Panel:
    # Reuse _check_vercel, _check_git from devops module
    # Return Rich Panel with Table inside

def collect_revenue() -> Panel:
    # Load ledger.json, compute total/month/count
    # Return Panel with summary text

def collect_agents() -> Panel:
    # Check engine availability, LLM key, data dir
    # Return Panel with status rows

def collect_system() -> Panel:
    # subprocess checks for python/git/node/docker
    # Return Panel with Table
```

### Step 2: Create `src/commands/dashboard.py` (~110 lines)

Core approach: `Rich.Live` + `Rich.Layout` + `threading` for keyboard input.

```python
import threading
from rich.live import Live
from rich.layout import Layout

def _build_layout(focused: int = 0) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="top", ratio=2),
        Layout(name="bottom", ratio=2),
        Layout(name="footer", size=3),
    )
    layout["top"].split_row(Layout(name="devops"), Layout(name="revenue"))
    layout["bottom"].split_row(Layout(name="agents"), Layout(name="system"))
    # Populate each slot from collectors
    # If focused != 0, expand that panel to full width
    return layout

def _key_listener(state: dict) -> None:
    """Thread reading single chars via tty raw mode."""
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while state["running"]:
            ch = sys.stdin.read(1)
            if ch in ("q", "\x03"):  # q or Ctrl+C
                state["running"] = False
            elif ch == "r":
                state["refresh"] = True
            elif ch in "01234":
                state["focused"] = int(ch)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

@dashboard_app.command()  # or direct function
def dash(refresh: int = 30):
    state = {"running": True, "refresh": False, "focused": 0}
    listener = threading.Thread(target=_key_listener, args=(state,), daemon=True)
    listener.start()
    with Live(auto_refresh=False, console=console) as live:
        while state["running"]:
            live.update(_build_layout(state["focused"]))
            live.refresh()
            # Sleep in small increments for responsive key handling
            for _ in range(refresh * 10):
                if not state["running"] or state["refresh"]:
                    break
                time.sleep(0.1)
            state["refresh"] = False
```

### Step 3: Register in `src/main.py` (2 lines)

```python
from src.commands.dashboard import dash
app.command(name="dash")(dash)
```

## Success Criteria

- `mekon dash` launches live TUI with 4 panels
- Panels update every 30s (configurable via `--refresh`)
- `q` exits cleanly, `r` forces refresh, `1-4` focuses panel
- No new dependencies (Rich Layout+Live already in `rich>=13.7.0`)
- Works on macOS/Linux terminals (tty raw mode); graceful fallback on Windows
