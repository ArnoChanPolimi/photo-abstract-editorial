from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

from app.analyzer import analyze_photo, open_normalized_image
from app.compositor import WORKING_WIDTH, render_variants
from app.generator import generate_job
from app.style_presets import PRESETS, get_preset


class PipelineTest(unittest.TestCase):
    def _create_source(self, path: Path) -> Image.Image:
        image = Image.new("RGB", (640, 400), "#A9C6D8")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 220, 640, 400), fill="#75835D")
        draw.rectangle((90, 120, 500, 300), fill="#B9B19F")
        draw.line((320, 40, 320, 330), fill="#4E453D", width=14)
        image.save(path)
        return image

    def test_all_presets_and_both_modes_export(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.png"
            self._create_source(source)

            result = generate_job(
                upload_path=None,
                local_path=str(source),
                styles=[preset.label for preset in PRESETS.values()],
                output_mode="Both",
                formats=["PNG", "PDF"],
                title_mode="Auto",
                abstraction_level="Medium",
                canvas_ratio="Portrait 2:3",
                output_root=root / "outputs",
            )

            self.assertEqual(len(result.previews), len(PRESETS) * 2)
            self.assertTrue(result.archive.exists())
            self.assertTrue((result.job_dir / "manifest.json").exists())
            metadata = json.loads((result.job_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["output_mode"], "Both")
            self.assertEqual(len(metadata["styles"]), len(PRESETS))
            with zipfile.ZipFile(result.archive) as archive:
                names = archive.namelist()
                self.assertTrue(any(name.endswith("__all-results.pdf") for name in names))
                self.assertTrue(any("__abstract.png" in name for name in names))
                self.assertTrue(any("__composed.png" in name for name in names))

    def test_composed_photo_region_is_deterministic_resize(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = Path(temporary) / "source.png"
            self._create_source(source_path)
            source = open_normalized_image(str(source_path))
            analysis = analyze_photo(source)
            rendered = render_variants(
                source, analysis, get_preset("Classic Editorial"),
                "Composed Editorial", "None", "", "Portrait 2:3", False,
            )[0].image
            expected_height = round(source.height * WORKING_WIDTH / source.width)
            expected = source.resize((WORKING_WIDTH, expected_height), Image.Resampling.LANCZOS)
            actual = rendered.crop((0, 0, WORKING_WIDTH, expected_height))
            self.assertEqual(actual.tobytes(), expected.tobytes())

    def test_transparent_abstract_has_alpha(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = Path(temporary) / "source.png"
            self._create_source(source_path)
            source = open_normalized_image(str(source_path))
            analysis = analyze_photo(source)
            rendered = render_variants(
                source, analysis, get_preset("Minimal"),
                "Abstract Panel Only", "Auto", "", "Square 1:1", True,
            )[0]
            self.assertEqual(rendered.image.mode, "RGBA")
            self.assertEqual(rendered.title, None)
            self.assertLess(rendered.image.getchannel("A").getextrema()[0], 255)


if __name__ == "__main__":
    unittest.main()
