"""Load the skill text and structured presets for local application use."""

from __future__ import annotations

from pathlib import Path

from .style_presets import PRESETS


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def load_skill_text() -> str:
    return (REPOSITORY_ROOT / "SKILL.md").read_text(encoding="utf-8")


def load_reference_prompt(language: str = "en") -> str:
    filename = (
        "photo-abstract-editorial-prompt.zh-CN.md"
        if language.lower().startswith("zh")
        else "photo-abstract-editorial-prompt.en.md"
    )
    return (REPOSITORY_ROOT / "references" / filename).read_text(encoding="utf-8")


def preset_manifest() -> list[dict[str, object]]:
    return [preset.public_dict() for preset in PRESETS.values()]
