"""Configuration loading utilities."""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class Config(BaseModel):
    """Application configuration."""

    system: dict[str, Any]
    agents: dict[str, Any]
    openrouter: dict[str, Any]
    memory: dict[str, Any]
    safety: dict[str, Any]
    associative: dict[str, Any]
    logging: dict[str, Any]
    metrics: dict[str, Any]


def load_config(config_path: str | None = None) -> Config:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file. If None, uses config/default.yaml

    Returns:
        Loaded configuration object

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    if config_path is None:
        # Default to config/default.yaml relative to project root
        project_root = Path(__file__).parent.parent.parent.parent
        config_path = str(project_root / "config" / "default.yaml")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path) as f:
        config_data = yaml.safe_load(f)

    return Config(**config_data)
