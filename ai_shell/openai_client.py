import os
import sys
from typing import Any, Dict, Generator, List, Optional

from dotenv import load_dotenv
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


def build_client() -> OpenAI:
    # Load .env if present to ease local dev
    load_dotenv()
    try:
        client = OpenAI()
        return client
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        print("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
        sys.exit(1)


def list_models(client: OpenAI) -> List[str]:
    try:
        resp = client.models.list()
        # Return model ids sorted
        ids = sorted([m.id for m in resp.data])
        return ids
    except Exception:
        return []


@retry(wait=wait_exponential(multiplier=1, min=1, max=30), stop=stop_after_attempt(3))
def chat_completion(
    client: OpenAI,
    *,
    messages: List[Dict[str, Any]],
    model: str,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> Dict[str, Any]:
    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def stream_chat_completion(
    client: OpenAI,
    *,
    messages: List[Dict[str, Any]],
    model: str,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
) -> Generator[Any, None, None]:
    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )

