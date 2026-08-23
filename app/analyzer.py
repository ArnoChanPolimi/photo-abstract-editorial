"""Deterministic photo analysis used to drive local abstract rendering."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import numpy as np
from PIL import Image, ImageOps

from .utils import stable_seed


@dataclass(frozen=True)
class PhotoAnalysis:
    width: int
    height: int
    orientation: str
    palette: tuple[tuple[int, int, int], ...]
    horizontal_axes: tuple[float, ...]
    vertical_axes: tuple[float, ...]
    luminance: float
    contrast: float
    seed: int


def open_normalized_image(source: str) -> Image.Image:
    image = Image.open(source)
    image = ImageOps.exif_transpose(image)
    return image.convert("RGB")


def _palette(image: Image.Image, count: int = 6) -> tuple[tuple[int, int, int], ...]:
    thumb = image.copy()
    thumb.thumbnail((320, 320), Image.Resampling.LANCZOS)
    quantized = thumb.quantize(colors=count, method=Image.Quantize.MEDIANCUT)
    raw_palette = quantized.getpalette() or []
    colors = quantized.getcolors() or []
    colors.sort(reverse=True)
    result: list[tuple[int, int, int]] = []
    for _, index in colors:
        rgb = tuple(raw_palette[index * 3:index * 3 + 3])
        if len(rgb) == 3:
            result.append(rgb)  # type: ignore[arg-type]
    return tuple(result or [(120, 120, 120)])


def _axis_peaks(values: np.ndarray, count: int) -> tuple[float, ...]:
    if values.size == 0:
        return (0.5,)
    minimum_gap = max(1, values.size // 8)
    candidates = np.argsort(values)[::-1]
    selected: list[int] = []
    for candidate in candidates:
        position = int(candidate)
        if all(abs(position - existing) >= minimum_gap for existing in selected):
            selected.append(position)
        if len(selected) == count:
            break
    return tuple(sorted((position + 1) / (values.size + 1) for position in selected))


def analyze_photo(image: Image.Image) -> PhotoAnalysis:
    sample = ImageOps.grayscale(image.copy())
    sample.thumbnail((480, 480), Image.Resampling.LANCZOS)
    array = np.asarray(sample, dtype=np.float32) / 255.0
    horizontal_energy = np.abs(np.diff(array, axis=0)).mean(axis=1)
    vertical_energy = np.abs(np.diff(array, axis=1)).mean(axis=0)
    with BytesIO() as buffer:
        image.save(buffer, format="PNG")
        seed = stable_seed(buffer.getvalue())
    orientation = "landscape" if image.width > image.height * 1.12 else (
        "portrait" if image.height > image.width * 1.12 else "square"
    )
    return PhotoAnalysis(
        width=image.width,
        height=image.height,
        orientation=orientation,
        palette=_palette(image),
        horizontal_axes=_axis_peaks(horizontal_energy, 3),
        vertical_axes=_axis_peaks(vertical_energy, 3),
        luminance=float(array.mean()),
        contrast=float(array.std()),
        seed=seed,
    )
