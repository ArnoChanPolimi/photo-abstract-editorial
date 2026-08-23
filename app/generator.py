"""End-to-end generation service used by both tests and Gradio."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .analyzer import analyze_photo, open_normalized_image
from .compositor import RenderedVariant, render_variants
from .exporters import export_variants
from .style_presets import get_preset
from .utils import create_job_dir, validate_local_image


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = REPOSITORY_ROOT / "outputs"


@dataclass(frozen=True)
class GenerationResult:
    job_id: str
    job_dir: Path
    previews: list[tuple[str, str]]
    files: list[Path]
    archive: Path
    source_path: Path


def resolve_input(upload_path: str | None, local_path: str) -> tuple[Path, str]:
    if upload_path:
        path = Path(upload_path)
        if not path.exists():
            raise ValueError("The uploaded image is no longer available. Please upload it again.")
        note = "Uploaded image used; local path ignored." if local_path.strip() else "Uploaded image used."
        return path.resolve(), note
    return validate_local_image(local_path), "Local path image used."


def generate_job(
    upload_path: str | None,
    local_path: str,
    styles: list[str],
    output_mode: str,
    formats: list[str],
    title_mode: str = "Auto",
    custom_title: str = "",
    abstraction_level: str = "Medium",
    canvas_ratio: str = "Portrait 2:3",
    transparent_abstract: bool = False,
    output_root: Path | None = None,
) -> GenerationResult:
    source_path, source_note = resolve_input(upload_path, local_path)
    if not styles:
        raise ValueError("Select at least one style preset.")
    if not formats:
        raise ValueError("Select at least one output format.")
    allowed_modes = {"Composed Editorial", "Abstract Panel Only", "Both"}
    if output_mode not in allowed_modes:
        raise ValueError(f"Unsupported output mode: {output_mode}")

    source = open_normalized_image(str(source_path))
    analysis = analyze_photo(source)
    job_id, job_dir = create_job_dir(output_root or DEFAULT_OUTPUT_ROOT, source_path.stem)
    abstraction_adjustments = {"Low": -0.14, "Medium": 0.0, "High": 0.14}
    variants: list[RenderedVariant] = []
    selected_presets: list[dict[str, object]] = []
    for style in styles:
        preset = get_preset(style)
        adjustment = abstraction_adjustments.get(abstraction_level, 0.0)
        preset = type(preset)(**{
            **preset.public_dict(),
            "abstraction": max(0.25, min(0.90, preset.abstraction + adjustment)),
        })
        selected_presets.append(preset.public_dict())
        variants.extend(render_variants(
            source, analysis, preset, output_mode, title_mode, custom_title,
            canvas_ratio, transparent_abstract,
        ))

    metadata: dict[str, object] = {
        "job_id": job_id,
        "source": str(source_path),
        "source_priority": source_note,
        "styles": selected_presets,
        "output_mode": output_mode,
        "formats": formats,
        "title_mode": title_mode,
        "custom_title": custom_title if title_mode == "Custom" else None,
        "abstraction_level": abstraction_level,
        "canvas_ratio": canvas_ratio,
        "transparent_abstract": transparent_abstract,
        "analysis": {
            "orientation": analysis.orientation,
            "source_size": [analysis.width, analysis.height],
            "palette": analysis.palette,
            "horizontal_axes": analysis.horizontal_axes,
            "vertical_axes": analysis.vertical_axes,
        },
    }
    files, archive, _ = export_variants(variants, job_dir, source_path.stem, formats, metadata)

    previews: list[tuple[str, str]] = []
    for variant in variants:
        preview_path = job_dir / f"{source_path.stem.lower()}__{variant.style_key}__{variant.mode}__preview.png"
        variant.image.save(preview_path, "PNG", optimize=True)
        label = f"{get_preset(variant.style_key).label} · {variant.mode.title()}"
        previews.append((str(preview_path), label))
    return GenerationResult(job_id, job_dir, previews, files, archive, source_path)
