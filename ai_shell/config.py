import json
import os
import sys
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

from platformdirs import user_config_dir, user_data_dir


APP_NAME = "ai-shell"
APP_AUTHOR = "ai-shell"


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def config_dir() -> str:
    override = os.getenv("AI_SHELL_CONFIG_DIR")
    path = override or user_config_dir(APP_NAME, APP_AUTHOR)
    _ensure_dir(path)
    return path


def data_dir() -> str:
    override = os.getenv("AI_SHELL_DATA_DIR")
    path = override or user_data_dir(APP_NAME, APP_AUTHOR)
    _ensure_dir(path)
    return path


def sessions_dir() -> str:
    path = os.path.join(data_dir(), "sessions")
    _ensure_dir(path)
    return path


def logs_dir() -> str:
    path = os.path.join(data_dir(), "logs")
    _ensure_dir(path)
    return path


def config_path() -> str:
    return os.path.join(config_dir(), "config.json")


@dataclass
class AppConfig:
    model: str = "gpt-4.1-mini"
    temperature: float = 0.7
    system_prompt: str = "You are a helpful AI assistant."
    stream: bool = True
    save_history: bool = True
    max_tokens: Optional[int] = None

    @classmethod
    def load(cls) -> "AppConfig":
        path = config_path()
        if not os.path.exists(path):
            return cls()
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**data)
        except Exception:
            # On any failure, return defaults. We intentionally avoid crashing on bad config.
            return cls()

    def save(self) -> None:
        path = config_path()
        _ensure_dir(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def update_from_pairs(self, pairs: Dict[str, str]) -> None:
        for k, v in pairs.items():
            if not hasattr(self, k):
                continue
            current = getattr(self, k)
            casted: Any = v
            if isinstance(current, bool):
                casted = v.lower() in ("1", "true", "yes", "on")
            elif isinstance(current, int):
                try:
                    casted = int(v)
                except ValueError:
                    continue
            elif isinstance(current, float):
                try:
                    casted = float(v)
                except ValueError:
                    continue
            setattr(self, k, casted)
