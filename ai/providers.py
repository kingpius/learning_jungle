import json
import os
import urllib.error
import urllib.request
from typing import Optional

from .exceptions import AIProviderError


def _is_gemini(url: str) -> bool:
    return "generativelanguage.googleapis.com" in url


def _build_gemini_request(
    *, base_url: str, api_key: str, prompt: str, seed: str
) -> urllib.request.Request:
    """
    Shapes the payload for Google Gemini's generateContent endpoint.
    """
    url = f"{base_url}?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.0,
            "topK": 1,
            "topP": 1,
            "seed": seed,
        },
        "safetySettings": [],
    }
    data = json.dumps(body).encode("utf-8")
    return urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
        },
    )


def _parse_gemini_response(body: bytes) -> str:
    try:
        payload = json.loads(body.decode("utf-8"))
        candidates = payload.get("candidates", [])
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        text = parts[0].get("text")
    except Exception as exc:
        raise AIProviderError("Invalid Gemini response.") from exc
    if not text:
        raise AIProviderError("Gemini response missing text.")
    return text


def _build_generic_request(
    *, base_url: str, api_key: str, model: str, prompt: str, seed: str
) -> urllib.request.Request:
    payload = {
        "model": model,
        "prompt": prompt,
        "seed": seed,
        "temperature": 0.0,
        "n": 1,
    }
    data = json.dumps(payload).encode("utf-8")
    return urllib.request.Request(
        base_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )


def call_llm(prompt: str, *, seed: str, timeout: Optional[int] = None) -> str:
    """
    Minimal HTTP client for LLM provider calls.
    Endpoint + credentials are provided via environment variables.
    Supports Gemini generateContent or a generic bearer-style JSON API.
    """
    base_url = os.environ.get("AI_PROVIDER_URL")
    api_key = os.environ.get("AI_API_KEY")
    model = os.environ.get("AI_MODEL", "default-model")
    if not base_url or not api_key:
        raise AIProviderError("AI provider configuration is missing.")

    is_gemini = _is_gemini(base_url)
    request = (
        _build_gemini_request(base_url=base_url, api_key=api_key, prompt=prompt, seed=seed)
        if is_gemini
        else _build_generic_request(base_url=base_url, api_key=api_key, model=model, prompt=prompt, seed=seed)
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            if is_gemini:
                return _parse_gemini_response(body)
            return body.decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise AIProviderError(f"Provider HTTP error: {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise AIProviderError("Provider unreachable.") from exc
