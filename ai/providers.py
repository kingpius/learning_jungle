import json
import os
import urllib.error
import urllib.request
from typing import Optional

from .exceptions import AIProviderError


def call_llm(prompt: str, *, seed: str, timeout: Optional[int] = None) -> str:
    """
    Minimal HTTP client for LLM provider calls.
    Endpoint + credentials are provided via environment variables.
    """
    base_url = os.environ.get("AI_PROVIDER_URL")
    api_key = os.environ.get("AI_API_KEY")
    model = os.environ.get("AI_MODEL", "default-model")
    if not base_url or not api_key:
        raise AIProviderError("AI provider configuration is missing.")

    payload = {
        "model": model,
        "prompt": prompt,
        "seed": seed,
        "temperature": 0.0,
        "n": 1,
    }
    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        base_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise AIProviderError(f"Provider HTTP error: {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise AIProviderError("Provider unreachable.") from exc
