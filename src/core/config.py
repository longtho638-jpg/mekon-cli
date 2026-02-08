"""Configuration management for Mekon CLI."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class MekonConfig(BaseSettings):
    """Central configuration loaded from environment and .env file."""

    # LLM settings
    llm_api_url: str = Field(default="https://api.openai.com/v1", alias="MEKON_LLM_API_URL")
    llm_api_key: str = Field(default="", alias="MEKON_LLM_API_KEY")
    llm_model: str = Field(default="gpt-4", alias="MEKON_LLM_MODEL")

    # Mekong CLI integration path
    mekong_cli_path: str = Field(default="../mekong-cli", alias="MEKONG_CLI_PATH")

    # DevOps tokens
    vercel_token: str = Field(default="", alias="VERCEL_TOKEN")
    cloudflare_token: str = Field(default="", alias="CLOUDFLARE_TOKEN")

    # Data directory
    data_dir: str = Field(default="~/.mekon", alias="MEKON_DATA_DIR")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @property
    def data_path(self) -> Path:
        """Resolved data directory path."""
        return Path(self.data_dir).expanduser()

    @property
    def mekong_path(self) -> Path:
        """Resolved mekong-cli project path."""
        return Path(self.mekong_cli_path).resolve()

    def ensure_data_dir(self) -> Path:
        """Create data directory if it doesn't exist."""
        self.data_path.mkdir(parents=True, exist_ok=True)
        return self.data_path


def get_config() -> MekonConfig:
    """Get the global configuration instance."""
    return MekonConfig()
