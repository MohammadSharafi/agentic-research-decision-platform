from __future__ import annotations

import json
import os
from typing import Any

import requests

from app.config.settings import get_settings


DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


def openai_available() -> bool:
    settings = get_settings()
    provider = settings.model_provider.strip().lower()
    return bool(settings.openai_api_key and provider in {"", "mock", "openai"})


def openai_chat_text(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.2,
    max_tokens: int = 1400,
) -> str | None:
    settings = get_settings()
    provider = settings.model_provider.strip().lower()
    if not settings.openai_api_key or provider not in {"", "mock", "openai"}:
        return None

    model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()
        return str(data["choices"][0]["message"]["content"]).strip()
    except Exception:
        return None


def openai_chat_json(
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.15,
    max_tokens: int = 2200,
) -> dict[str, Any] | None:
    text = openai_chat_text(
        system_prompt,
        user_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if not text:
        return None
    return _parse_json_object(text)


def _parse_json_object(text: str) -> dict[str, Any] | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            parsed = json.loads(cleaned[start : end + 1])
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None
