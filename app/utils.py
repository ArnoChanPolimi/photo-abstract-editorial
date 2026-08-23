"""Small shared helpers with no UI dependencies."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from pathlib import Path
from uuid import uuid4


SUPPORTED_INPUTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}


def slugify(value: str, fallback: str = "image") -> str:
    value = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip()).strip("-").lower()
    return value or fallback


def create_job_dir(output_root: Path, input_stem: str) -> tuple[str, Path]:
    job_id = f"{datetime.now():%Y%m%d-%H%M%S}-{uuid4().hex[:8]}"
    directory = output_root / job_id / slugify(input_stem)
    directory.mkdir(parents=True, exist_ok=False)
    return job_id, directory


def stable_seed(data: bytes) -> int:
    return int.from_bytes(hashlib.sha256(data).digest()[:8], "big")


def validate_local_image(path_value: str) -> Path:
    raw = path_value.strip().strip('"').strip("'")
    if not raw:
        raise ValueError("No local image path was provided.")
    path = Path(raw).expanduser()
    if not path.exists():
        raise ValueError(f"Local image path does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Local image path is not a file: {path}")
    if path.suffix.lower() not in SUPPORTED_INPUTS:
        raise ValueError(
            f"Unsupported image type '{path.suffix}'. Supported: {', '.join(sorted(SUPPORTED_INPUTS))}"
        )
    return path.resolve()
