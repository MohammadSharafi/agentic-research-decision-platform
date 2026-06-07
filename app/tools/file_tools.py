from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any


def ensure_dir(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def write_json(path: str | Path, payload: dict[str, Any] | list[Any]) -> Path:
    target = Path(path)
    ensure_dir(target.parent)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_text(path: str | Path, content: str) -> Path:
    target = Path(path)
    ensure_dir(target.parent)
    target.write_text(content, encoding="utf-8")
    return target


def copy_file(src: str | Path, dst: str | Path) -> Path:
    target = Path(dst)
    ensure_dir(target.parent)
    shutil.copy2(src, target)
    return target

