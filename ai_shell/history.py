import datetime as dt
import json
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from .config import sessions_dir


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


@dataclass
class Message:
    role: str
    content: Any


@dataclass
class SessionRecord:
    id: str
    created_at: str
    model: str
    system_prompt: str
    messages: List[Message]

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "model": self.model,
            "system_prompt": self.system_prompt,
            "messages": [asdict(m) for m in self.messages],
        }


def new_session_id() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def save_session(record: SessionRecord) -> str:
    sid = record.id
    path = os.path.join(sessions_dir(), f"{sid}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record.to_json(), f, indent=2)
    return path


def list_sessions() -> List[str]:
    d = sessions_dir()
    try:
        files = [f for f in os.listdir(d) if f.endswith(".json")]
        files.sort(reverse=True)
        return files
    except FileNotFoundError:
        return []


def load_session(path_or_id: str) -> Optional[SessionRecord]:
    path = path_or_id
    if not os.path.exists(path):
        path = os.path.join(sessions_dir(), f"{path_or_id}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        messages = [Message(**m) for m in data.get("messages", [])]
        return SessionRecord(
            id=data.get("id", "unknown"),
            created_at=data.get("created_at", _now_iso()),
            model=data.get("model", "unknown"),
            system_prompt=data.get("system_prompt", ""),
            messages=messages,
        )
    except Exception:
        return None

