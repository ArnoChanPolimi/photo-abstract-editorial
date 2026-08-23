"""Structured, stable style presets shared by the UI and renderer."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class StylePreset:
    key: str
    label: str
    description: str
    background: str
    abstraction: float
    mark_family: str
    saturation: float
    contrast: float
    panel_ratio: float
    identity_cues: int
    person_simplification: float
    whitespace: float
    line_weight: int
    title_style: str

    def public_dict(self) -> dict[str, object]:
        return asdict(self)


PRESETS: dict[str, StylePreset] = {
    "classic-editorial": StylePreset(
        "classic-editorial", "Classic Editorial",
        "The original restrained photo-and-memory-panel language.",
        "#F3F0E8", 0.58, "architectural masses + fine axes", 0.68, 0.92,
        0.54, 2, 0.90, 0.72, 4, "book serif",
    ),
    "minimal": StylePreset(
        "minimal", "Minimal",
        "Fewer marks, quieter contrast, and substantially more whitespace.",
        "#F6F4EE", 0.78, "thin axes + sparse masses", 0.48, 0.70,
        0.60, 1, 0.96, 0.82, 3, "fine serif",
    ),
    "travel-architecture": StylePreset(
        "travel-architecture", "Travel / Architecture",
        "Stronger structural axes and a few controlled landmark cues.",
        "#F1EEE5", 0.48, "layered planes + structural axes", 0.72, 1.02,
        0.50, 3, 0.88, 0.68, 5, "book serif",
    ),
    "soft-memory": StylePreset(
        "soft-memory", "Soft Memory",
        "Airy, low-contrast overlapping forms with gentle visual pauses.",
        "#F7F1E8", 0.66, "soft organic masses", 0.50, 0.72,
        0.58, 1, 0.94, 0.78, 3, "humanist serif",
    ),
    "bold-graphic": StylePreset(
        "bold-graphic", "Bold Graphic",
        "Larger planar forms, stronger contrast, and a decisive silhouette.",
        "#EEEAE0", 0.45, "bold planar masses", 0.90, 1.22,
        0.47, 2, 0.86, 0.62, 7, "display serif",
    ),
    "museum-poster": StylePreset(
        "museum-poster", "Museum Poster",
        "Formal exhibition spacing with composed geometry and typography.",
        "#F2EFE7", 0.55, "curated planes + measured axes", 0.62, 0.98,
        0.57, 2, 0.91, 0.75, 4, "editorial serif",
    ),
}

LABEL_TO_KEY = {preset.label: key for key, preset in PRESETS.items()}


def get_preset(value: str) -> StylePreset:
    key = LABEL_TO_KEY.get(value, value)
    if key not in PRESETS:
        raise ValueError(f"Unknown style preset: {value}")
    return PRESETS[key]


def preset_choices() -> list[str]:
    return [preset.label for preset in PRESETS.values()]
