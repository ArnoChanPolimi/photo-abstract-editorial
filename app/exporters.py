"""Export rendered variants to selected formats and downloadable archives."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from PIL import Image

from .compositor import RenderedVariant
from .utils import slugify


FORMAT_EXTENSIONS = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp", "PDF": ".pdf"}


def _save_image(image: Image.Image, path: Path, file_format: str) -> None:
    if file_format == "PNG":
        image.save(path, "PNG", optimize=True)
    elif file_format == "JPEG":
        background = Image.new("RGB", image.size, "white")
        if image.mode == "RGBA":
            background.paste(image, mask=image.getchannel("A"))
        else:
            background.paste(image.convert("RGB"))
        background.save(path, "JPEG", quality=94, subsampling=0, optimize=True)
    elif file_format == "WEBP":
        image.save(path, "WEBP", quality=94, method=6)
    elif file_format == "PDF":
        background = Image.new("RGB", image.size, "white")
        if image.mode == "RGBA":
            background.paste(image, mask=image.getchannel("A"))
        else:
            background.paste(image.convert("RGB"))
        background.save(path, "PDF", resolution=150.0)
    else:
        raise ValueError(f"Unsupported output format: {file_format}")


def export_variants(
    variants: list[RenderedVariant],
    output_dir: Path,
    input_stem: str,
    formats: list[str],
    metadata: dict[str, object],
) -> tuple[list[Path], Path, Path | None]:
    files: list[Path] = []
    pdf_pages: list[Image.Image] = []
    base = slugify(input_stem)
    for variant in variants:
        for file_format in formats:
            extension = FORMAT_EXTENSIONS[file_format]
            filename = f"{base}__{variant.style_key}__{variant.mode}{extension}"
            path = output_dir / filename
            _save_image(variant.image, path, file_format)
            files.append(path)
        if "PDF" in formats:
            page = Image.new("RGB", variant.image.size, "white")
            if variant.image.mode == "RGBA":
                page.paste(variant.image, mask=variant.image.getchannel("A"))
            else:
                page.paste(variant.image.convert("RGB"))
            pdf_pages.append(page)

    summary_pdf: Path | None = None
    if len(pdf_pages) > 1:
        summary_pdf = output_dir / f"{base}__all-results.pdf"
        pdf_pages[0].save(summary_pdf, "PDF", save_all=True, append_images=pdf_pages[1:], resolution=150.0)
        files.append(summary_pdf)

    manifest = output_dir / "manifest.json"
    manifest.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    files.append(manifest)

    archive = output_dir / f"{base}__all-results.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for file in files:
            bundle.write(file, arcname=file.name)
    return files, archive, summary_pdf
