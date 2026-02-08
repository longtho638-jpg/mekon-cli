"""Activity logger for Mekon CLI - records actions to JSONL file."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.core.config import get_config


class ActivityLogger:
    """Log mekon CLI activity to ~/.mekon/logs/activity.jsonl"""

    def __init__(self) -> None:
        config = get_config()
        self.log_dir: Path = config.data_path / "logs"
        self.log_file: Path = self.log_dir / "activity.jsonl"

    def log(self, action: str, details: str = "", status: str = "ok") -> None:
        """Append a single log entry."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
            "status": status,
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def read(self, limit: int = 50) -> list[dict[str, str]]:
        """Read last N log entries."""
        if not self.log_file.exists():
            return []
        lines = self.log_file.read_text().strip().split("\n")
        entries = [json.loads(line) for line in lines if line.strip()]
        return entries[-limit:]

    def clear(self) -> int:
        """Clear all logs. Returns count of entries cleared."""
        if not self.log_file.exists():
            return 0
        lines = self.log_file.read_text().strip().split("\n")
        count = len([line for line in lines if line.strip()])
        self.log_file.unlink()
        return count


def get_logger() -> ActivityLogger:
    """Get a new ActivityLogger instance."""
    return ActivityLogger()
