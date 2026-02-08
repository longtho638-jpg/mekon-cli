# Code Standards

## Language & Style
- Python 3.9+ with `from __future__ import annotations` for modern type hints
- Line length: 100 chars (ruff)
- Type hints required on all public functions
- Docstrings on all modules and public classes/functions

## File Naming
- Python package modules: snake_case (required by Python import system)
- Standalone scripts: kebab-case with descriptive names
- Docs/plans: kebab-case markdown

## Architecture Patterns
- **Typer sub-apps**: Each domain group is a `typer.Typer()` instance registered on `main.app`
- **Rich console**: Single shared `console` instance from `src.core.console`
- **Pydantic config**: All settings via `MekonConfig` from environment/.env
- **Engine bridge**: Lazy import of mekong-cli modules through `src.core.engine`

## Adding a New Command Group
1. Create `src/commands/your_domain.py`
2. Define `your_app = typer.Typer(help="...")`
3. Add commands as `@your_app.command()`
4. Register in `src/main.py`: `app.add_typer(your_app, name="your-domain")`
5. Add tests in `tests/`

## Error Handling
- Use `error_panel()` for user-facing errors
- Raise `typer.Exit(code=1)` for non-zero exits
- Wrap subprocess calls in try/except for FileNotFoundError + TimeoutExpired

## Testing
- Use `typer.testing.CliRunner` for CLI integration tests
- Test structure: `TestGroupCommands` classes per domain
- No mocks for CLI tests — test actual command output
