"""Deterministic abstract rendering and faithful photo compositing."""

from __future__ import annotations

import colorsys
import random
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont

from .analyzer import PhotoAnalysis
from .style_presets import StylePreset


WORKING_WIDTH = 1200


@dataclass(frozen=True)
class RenderedVariant:
    style_key: str
    mode: str
    image: Image.Image
    title: str | None


def _luminance(color: tuple[int, int, int]) -> float:
    return 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]


def _tune_color(color: tuple[int, int, int], saturation: float, contrast: float) -> tuple[int, int, int]:
    r, g, b = (channel / 255 for channel in color)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    s = max(0.0, min(1.0, s * saturation))
    v = max(0.08, min(0.92, 0.5 + (v - 0.5) * contrast))
    return tuple(round(channel * 255) for channel in colorsys.hsv_to_rgb(h, s, v))


def _render_palette(analysis: PhotoAnalysis, preset: StylePreset) -> list[tuple[int, int, int]]:
    colors = [_tune_color(color, preset.saturation, preset.contrast) for color in analysis.palette]
    colors.sort(key=_luminance)
    if len(colors) < 4:
        colors.extend([(78, 74, 68), (156, 151, 139), (199, 195, 183), (112, 126, 91)])
    return colors


def _font(size: int, italic: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/georgiai.ttf" if italic else "C:/Windows/Fonts/georgia.ttf"),
        Path("C:/Windows/Fonts/timesi.ttf" if italic else "C:/Windows/Fonts/times.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf" if italic else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def auto_title(analysis: PhotoAnalysis, preset: StylePreset) -> str:
    light = ("Quiet Light", "Light Between Forms", "A Measure of Day")
    dark = ("Held in Shadow", "The Weight Between", "After the Long Shade")
    structural = ("Lines Find Their Place", "Between Axis and Air", "Forms in Passing")
    options = structural if preset.identity_cues >= 2 else (light if analysis.luminance >= 0.52 else dark)
    return options[(analysis.seed + len(preset.key)) % len(options)]


def _panel_share(analysis: PhotoAnalysis, preset: StylePreset) -> float:
    if analysis.orientation == "portrait":
        return max(0.32, min(0.45, preset.panel_ratio - 0.14))
    if analysis.orientation == "square":
        return max(0.42, min(0.52, preset.panel_ratio - 0.05))
    return max(0.48, min(0.62, preset.panel_ratio))


def _standalone_size(canvas_ratio: str) -> tuple[int, int]:
    return {
        "Portrait 2:3": (WORKING_WIDTH, 1800),
        "Square 1:1": (WORKING_WIDTH, WORKING_WIDTH),
        "Landscape 3:2": (WORKING_WIDTH, 800),
    }.get(canvas_ratio, (WORKING_WIDTH, 1500))


def _draw_motif(
    canvas: Image.Image,
    analysis: PhotoAnalysis,
    preset: StylePreset,
    title: str | None,
    transparent: bool,
) -> None:
    draw = ImageDraw.Draw(canvas, "RGBA")
    width, height = canvas.size
    palette = _render_palette(analysis, preset)
    dark, mid, light = palette[0], palette[len(palette) // 2], palette[-1]
    accent = max(palette, key=lambda c: max(c) - min(c))
    rng = random.Random(analysis.seed ^ sum(ord(char) for char in preset.key))

    title_zone = int(height * 0.24) if title else int(height * 0.08)
    usable_bottom = height - title_zone
    motif_height = int(usable_bottom * (0.24 + (1 - preset.whitespace) * 0.45))
    motif_width = int(width * (0.32 + (1 - preset.whitespace) * 0.90))
    motif_width = max(int(width * 0.30), min(int(width * 0.68), motif_width))
    left = (width - motif_width) // 2
    baseline = int(usable_bottom * 0.73)
    top = max(int(height * 0.18), baseline - motif_height)

    mass_count = max(2, min(5, round(6 - preset.abstraction * 4)))
    axes = analysis.vertical_axes or (0.33, 0.62)
    for index in range(mass_count):
        axis = axes[index % len(axes)]
        center = left + int(motif_width * (0.12 + axis * 0.76))
        block_w = int(motif_width * rng.uniform(0.20, 0.38))
        block_h = int(motif_height * rng.uniform(0.30, 0.78))
        x0 = max(left, center - block_w // 2)
        x1 = min(left + motif_width, x0 + block_w)
        y1 = baseline - rng.randint(0, max(1, motif_height // 8))
        y0 = max(top, y1 - block_h)
        color = (light, mid, accent, palette[min(index, len(palette) - 1)])[index % 4]
        alpha = 215 if preset.key == "bold-graphic" else (135 if preset.key == "soft-memory" else 178)
        if preset.mark_family == "soft organic masses":
            draw.ellipse((x0, y0, x1, y1), fill=(*color, alpha))
        elif preset.key == "bold-graphic":
            cut = int(block_w * 0.16)
            draw.polygon([(x0, y1), (x0 + cut, y0), (x1, y0), (x1, y1)], fill=(*color, alpha))
        else:
            offset = int(block_h * rng.uniform(-0.12, 0.12))
            draw.polygon([(x0, y1), (x0, y0 + offset), (x1, y0), (x1, y1)], fill=(*color, alpha))

    axis_color = (*dark, 190 if transparent else 165)
    horizontal_count = 1 if preset.key == "minimal" else 2
    for index, axis in enumerate(analysis.horizontal_axes[:horizontal_count]):
        y = top + int((0.25 + axis * 0.60) * motif_height)
        inset = int(motif_width * (0.03 + index * 0.08))
        draw.line((left + inset, y, left + motif_width - inset, y), fill=axis_color, width=preset.line_weight)
    vertical_count = min(preset.identity_cues, len(analysis.vertical_axes))
    for index, axis in enumerate(analysis.vertical_axes[:vertical_count]):
        x = left + int(axis * motif_width)
        y0 = top + int(motif_height * (0.10 + index * 0.08))
        draw.line((x, baseline, x, y0), fill=axis_color, width=preset.line_weight)
        branch = int(motif_width * (0.08 + index * 0.025))
        direction = -1 if index % 2 == 0 else 1
        draw.line((x, y0 + motif_height * 0.22, x + direction * branch, y0), fill=axis_color, width=max(2, preset.line_weight - 1))

    band_y = baseline + int(motif_height * 0.03)
    band_h = max(8, int(motif_height * (0.04 if preset.key == "minimal" else 0.09)))
    draw.polygon(
        [(left, band_y), (left + motif_width, band_y - band_h // 4),
         (left + motif_width, band_y + band_h), (left, band_y + band_h * 3 // 4)],
        fill=(*accent, 185),
    )

    if title:
        font_size = max(28, int(width * (0.035 if preset.key == "minimal" else 0.043)))
        font = _font(font_size)
        box = draw.textbbox((0, 0), title, font=font)
        text_width = box[2] - box[0]
        text_y = height - int(title_zone * 0.52)
        draw.text(((width - text_width) // 2, text_y), title, font=font, fill=(*dark, 235))


def render_abstract_panel(
    analysis: PhotoAnalysis,
    preset: StylePreset,
    size: tuple[int, int],
    title: str | None,
    transparent: bool = False,
) -> Image.Image:
    if transparent:
        canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    else:
        canvas = Image.new("RGB", size, ImageColor.getrgb(preset.background))
    _draw_motif(canvas, analysis, preset, title, transparent)
    return canvas


def render_variants(
    source: Image.Image,
    analysis: PhotoAnalysis,
    preset: StylePreset,
    output_mode: str,
    title_mode: str,
    custom_title: str,
    canvas_ratio: str,
    transparent_abstract: bool,
) -> list[RenderedVariant]:
    title = None if title_mode == "None" else (
        custom_title.strip() if title_mode == "Custom" and custom_title.strip() else auto_title(analysis, preset)
    )
    modes = ["composed", "abstract"] if output_mode == "Both" else [
        "abstract" if output_mode == "Abstract Panel Only" else "composed"
    ]
    results: list[RenderedVariant] = []
    photo_width = WORKING_WIDTH
    photo_height = round(source.height * photo_width / source.width)
    photo = source.resize((photo_width, photo_height), Image.Resampling.LANCZOS)

    for mode in modes:
        if mode == "abstract":
            size = _standalone_size(canvas_ratio)
            standalone_title = None if transparent_abstract else title
            panel = render_abstract_panel(analysis, preset, size, standalone_title, transparent_abstract)
            results.append(RenderedVariant(preset.key, mode, panel, standalone_title))
            continue
        share = _panel_share(analysis, preset)
        panel_height = round(photo_height * share / (1 - share))
        panel = render_abstract_panel(analysis, preset, (photo_width, panel_height), title, False)
        composition = Image.new("RGB", (photo_width, photo_height + panel_height), preset.background)
        composition.paste(photo, (0, 0))
        composition.paste(panel.convert("RGB"), (0, photo_height))
        results.append(RenderedVariant(preset.key, mode, composition, title))
    return results
