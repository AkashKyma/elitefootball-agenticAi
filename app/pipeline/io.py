from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_json(path: str | Path) -> Any:
    from app.storage import get_default_provider
    return get_default_provider().read_json(str(path))


def write_json(path: str | Path, payload: Any) -> str:
    import os, sys
    from app.storage import get_default_provider
    output_path = Path(path)
    if "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
        output_path = Path("data/test") / output_path.name
    return get_default_provider().write_json(str(output_path), payload)


def list_files(directory: str | Path, pattern: str) -> list[Path]:
    path = Path(directory)
    if not path.exists():
        return []
    return sorted(path.glob(pattern))
