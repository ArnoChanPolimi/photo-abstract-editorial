"""Gradio interface for the local Photo Abstract Editorial application."""

from __future__ import annotations

from pathlib import Path

import gradio as gr

from .analyzer import open_normalized_image
from .generator import generate_job
from .style_presets import PRESETS, preset_choices
from .utils import validate_local_image


APP_CSS = """
.app-shell {max-width: 1320px; margin: 0 auto;}
.hero {padding: 18px 4px 6px;}
.hero h1 {font-family: Georgia, serif; font-weight: 500; letter-spacing: -.02em;}
.muted-card {border: 1px solid var(--border-color-primary); border-radius: 14px; padding: 12px;}
.generate-button {min-height: 48px; font-weight: 650;}
"""


def _style_help() -> str:
    rows = [f"**{preset.label}** — {preset.description}" for preset in PRESETS.values()]
    return "\n\n".join(rows)


def preview_local_path(path_value: str):
    try:
        path = validate_local_image(path_value)
        return open_normalized_image(str(path)), f"Ready: `{path}`"
    except Exception as error:
        raise gr.Error(str(error)) from error


def run_generation(
    upload_path: str | None,
    local_path: str,
    styles: list[str],
    output_mode: str,
    formats: list[str],
    title_mode: str,
    custom_title: str,
    abstraction_level: str,
    canvas_ratio: str,
    transparent_abstract: bool,
    progress=gr.Progress(track_tqdm=False),
):
    try:
        progress(0.08, desc="Validating input")
        progress(0.25, desc="Analyzing photo relationships")
        result = generate_job(
            upload_path=upload_path,
            local_path=local_path,
            styles=styles,
            output_mode=output_mode,
            formats=formats,
            title_mode=title_mode,
            custom_title=custom_title,
            abstraction_level=abstraction_level,
            canvas_ratio=canvas_ratio,
            transparent_abstract=transparent_abstract,
        )
        progress(1.0, desc="Export complete")
        status = (
            f"### Complete · `{result.job_id}`\n"
            f"Source: `{result.source_path}`  \n"
            f"Saved to: `{result.job_dir}`  \n"
            f"Generated {len(result.previews)} visual result(s) and {len(result.files)} downloadable file(s)."
        )
        return result.previews, [str(path) for path in result.files], str(result.archive), status
    except Exception as error:
        raise gr.Error(str(error)) from error


def build_app() -> gr.Blocks:
    with gr.Blocks(title="Photo Abstract Editorial") as demo:
        with gr.Column(elem_classes=["app-shell"]):
            gr.Markdown(
                "# Photo Abstract Editorial\n"
                "Turn one photograph into faithful composed editorials and standalone abstract memory panels. "
                "Everything runs locally; the photographic area is never AI-redrawn.",
                elem_classes=["hero"],
            )

            with gr.Row():
                with gr.Column(scale=5):
                    gr.Markdown("## 1 · Choose one source image")
                    upload = gr.Image(
                        label="Upload or drag an image (takes priority)",
                        type="filepath",
                        sources=["upload", "clipboard"],
                        height=330,
                    )
                    with gr.Row():
                        local_path = gr.Textbox(
                            label="Or enter a complete local image path",
                            placeholder=r"D:\Photos\example.jpg",
                            scale=5,
                        )
                        preview_button = gr.Button("Preview path", scale=1)
                    input_status = gr.Markdown(
                        "If both are provided, the uploaded image is used and the local path is ignored."
                    )
                    local_preview = gr.Image(label="Local path preview", visible=True, height=260)
                    preview_button.click(
                        preview_local_path,
                        inputs=[local_path],
                        outputs=[local_preview, input_status],
                    )

                with gr.Column(scale=5):
                    gr.Markdown("## 2 · Configure the result")
                    styles = gr.CheckboxGroup(
                        choices=preset_choices(),
                        value=["Classic Editorial"],
                        label="Style presets — select one or many",
                    )
                    with gr.Accordion("What each style changes", open=False):
                        gr.Markdown(_style_help())
                    output_mode = gr.Radio(
                        ["Composed Editorial", "Abstract Panel Only", "Both"],
                        value="Both",
                        label="Output mode",
                    )
                    formats = gr.CheckboxGroup(
                        ["PNG", "JPEG", "WEBP", "PDF"],
                        value=["PNG"],
                        label="Output formats — select one or many",
                    )
                    with gr.Row():
                        title_mode = gr.Radio(["Auto", "None", "Custom"], value="Auto", label="Title")
                        abstraction = gr.Radio(["Low", "Medium", "High"], value="Medium", label="Abstraction")
                    custom_title = gr.Textbox(
                        label="Custom English title",
                        placeholder="Used only when Title = Custom",
                    )
                    with gr.Row():
                        canvas_ratio = gr.Dropdown(
                            ["Portrait 2:3", "Square 1:1", "Landscape 3:2"],
                            value="Portrait 2:3",
                            label="Standalone canvas",
                        )
                        transparent = gr.Checkbox(
                            value=False,
                            label="Transparent standalone motif (title omitted)",
                        )
                    generate = gr.Button("Generate locally", variant="primary", elem_classes=["generate-button"])

            gr.Markdown("## 3 · Results")
            status = gr.Markdown("No task has been generated yet.", elem_classes=["muted-card"])
            gallery = gr.Gallery(label="Result gallery", columns=3, height="auto", object_fit="contain")
            with gr.Row():
                files = gr.Files(label="Download individual files")
                archive = gr.File(label="Download all results as ZIP")

            generate.click(
                run_generation,
                inputs=[
                    upload, local_path, styles, output_mode, formats, title_mode,
                    custom_title, abstraction, canvas_ratio, transparent,
                ],
                outputs=[gallery, files, archive, status],
            )
    return demo
