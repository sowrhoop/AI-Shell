import base64
import mimetypes
import os
from typing import Any, Dict, List, Tuple


def read_text_file(path: str, max_bytes: int = 200_000) -> str:
    with open(path, "rb") as f:
        data = f.read(max_bytes + 1)
    truncated = len(data) > max_bytes
    text = data[:max_bytes].decode("utf-8", errors="replace")
    if truncated:
        text += "\n\n[...snip: file truncated for length ...]"
    return text


def file_to_image_url(path: str) -> Tuple[str, str]:
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = "application/octet-stream"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    url = f"data:{mime};base64,{b64}"
    return url, mime


def build_user_content(text: str, image_paths: List[str]) -> List[Dict[str, Any]]:
    parts: List[Dict[str, Any]] = []
    if text.strip():
        parts.append({"type": "text", "text": text})
    for p in image_paths:
        url, _ = file_to_image_url(p)
        parts.append({"type": "image_url", "image_url": {"url": url}})
    return parts

