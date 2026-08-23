---
name: photo-abstract-editorial
description: Create either a complete photo-plus-abstraction editorial artwork, a standalone photo-derived abstract motif, or a matched set from one uploaded photograph. Use for abstract editorial diptychs, visual memory panels, minimalist archival posters, and editable vector motifs without redrawing or stylizing the source photo.
---

# Photo Abstract Editorial

Create selected editorial or standalone abstract deliverables from one uploaded photograph. Keep any displayed photograph faithful; derive every abstract output only from the photograph's observed spatial, tonal, and color relationships.

## Workflow

1. Inspect the photograph internally. Identify three to six decisive spatial facts: subject relationships, scale, axes, direction, intervals, overlap, depth, rhythm, light, color roles, and negative space.
2. Keep the photo as the upper or principal section. Permit only proportional scaling or a slight crop needed for the composition. Never redraw, extend, replace, retouch, apply a filter to, or otherwise alter its content.
3. Reconstruct the retained relationships below as a sparse abstract motif—not a thumbnail, trace, illustration, vector icon, or style transfer. Prefer relationships over silhouettes and preserve only the minimum recognition cues needed for distinctive subjects.
4. Select the requested output mode from [references/output-formats.md](references/output-formats.md): complete editorial work, standalone abstract motif, or both. For the complete work, use an untextured uniform ivory lower panel and adapt the photo/panel proportions to the photograph rather than splitting it mechanically in half. For a standalone output, omit the photograph and preserve the same distilled relationships as an independent composition.
5. Use one primary mark family and no more than two supporting families. Extract a muted palette solely from the photo; use generous whitespace and avoid invented decorative elements, colors, symbols, and symmetry.
6. Create one original English title of two to five words, grounded in visible facts. Place it only on the abstract panel in a restrained editorial serif face. Add a short subtitle only when it adds meaning.
7. Before production, honor any output mode and file format the user requested. If either is unspecified, briefly offer the combined choices in [references/output-formats.md](references/output-formats.md); do not silently assume that the complete photo-plus-panel composition or a raster preview is the only deliverable.
8. Return only the requested deliverables. Do not add design analysis, title options, labels, dates, logos, or watermarks to the artwork.

## Guardrails

- Treat the uploaded photo as the sole content source.
- Keep the panel background flat, continuous, and neutral ivory; exclude gradients, paper texture, grain, glow, shadows, vignettes, stains, collage artifacts, and scan effects.
- Make every abstract mark traceable to a visual fact in the source photo.
- Preserve people as irregular continuous short vertical marks or gently tapered blocks, never illustrated heads, limbs, faces, or clothing.
- Preserve landmark architecture with at most one to three identity cues; omit architectural surface detail.

## Reference Prompt

Read the appropriate full prompt before producing the image:

- Chinese: [references/photo-abstract-editorial-prompt.zh-CN.md](references/photo-abstract-editorial-prompt.zh-CN.md)
- English: [references/photo-abstract-editorial-prompt.en.md](references/photo-abstract-editorial-prompt.en.md)

Read [references/output-formats.md](references/output-formats.md) whenever selecting, generating, exporting, or explaining deliverable formats. Preserve the distinction between true vector artwork and a raster photograph embedded in an SVG or PDF.

Use [assets/examples](assets/examples) as visual input examples only. Do not reuse their subject matter, colors, or composition unless the user supplies that exact image.

## Local App Presets

The local web application uses the same invariants through structured presets in [app/style_presets.py](app/style_presets.py). `Classic Editorial` is the default expression of this skill. The additional `Minimal`, `Travel / Architecture`, `Soft Memory`, `Bold Graphic`, and `Museum Poster` presets may change abstraction, mark language, saturation, contrast, panel proportion, identity cues, whitespace, line weight, and typography—but never the sole-source rule or faithful-photo rule.

For local batch generation, keep the source photograph as original pixels and generate only the panel deterministically before compositing. This local renderer is a maintainable first-version interpretation of the skill, not an AI replacement for the full prompt-driven workflow.
