# Output Modes and Formats

Choose the product mode first and the file format second. Honor explicit user choices. If either choice is missing, offer a compact menu covering only the missing dimension.

## Product mode

1. **Complete editorial artwork** — the current photo-plus-abstract-panel composition: faithful photograph above or in the principal region, ivory abstract panel, and optional poetic title.
2. **Standalone abstract artwork** — omit the photograph and deliver only the photo-derived abstract motif. Offer either:
   - an ivory composition with generous whitespace and optional title; or
   - a transparent-background motif without a title, suitable for flexible placement and logo-like use.
3. **Matched set** — deliver both the complete editorial artwork and its standalone abstract counterpart, keeping motif geometry, palette, and title treatment consistent.

The standalone mode is not a generic logo generator. The uploaded photograph remains the sole content source, and every mark must remain traceable to its spatial, tonal, or color relationships. Do not crop the motif out of a generated raster panel; compose or reconstruct it intentionally for the standalone canvas.

## File format

1. **Screen image** — PNG (recommended) or JPEG.
2. **Print image** — high-resolution PNG or TIFF.
3. **Full-layout document** — print PDF and/or SVG containing the raster photograph plus vector-capable layout elements; this is not a fully vector artwork.
4. **Vector motif** — the abstract motif and optional title as true-vector SVG and/or vector PDF, without the photograph.
5. **Complete package** — full editorial artwork as PNG, print PDF, and a separate true-vector SVG/PDF motif.

Ask at most one short combined mode-and-format question when the choices materially change the workflow. If the user asks to proceed without choosing, default to a matched set: full artwork as PNG plus standalone motif as SVG and PNG. Do not offer formats that the available tools cannot actually create and verify.

## Format truthfulness

- The source photograph is raster content. A full composition exported as SVG or PDF still contains an embedded raster photograph; never describe it as fully vector.
- Only the abstract motif, geometric marks, lines, and outlined typography can be true vector.
- Do not convert a generated raster motif to SVG merely by embedding the bitmap or applying automatic tracing and call it vector. Reconstruct clean paths and verify that the SVG contains vector elements.
- For editable SVG, keep shapes as paths/primitives. Preserve text as editable text only when font availability is controlled; otherwise outline the final title and also record the title text separately in delivery notes.
- For PDF, state whether it is a vector-motif PDF, a print PDF containing the raster photograph, or both.

## Deliverable guidance

- **PNG:** lossless default for screen viewing and the full composition; preserve color fidelity.
- **JPEG:** optional lightweight preview; never use it as the only archival deliverable.
- **TIFF:** optional high-resolution print master when supported and requested.
- **SVG:** preferred editable vector source for the standalone abstract motif; use a correct `viewBox`, support transparent output when selected, and avoid linked local assets.
- **PDF:** use for print delivery or vector motif delivery; embed required fonts or outline title glyphs.

Use clear filenames that distinguish the artifacts, for example `title-editorial.png`, `title-print.pdf`, `title-abstract.png`, `title-motif.svg`, and `title-motif.pdf`. Verify that each requested file opens, has the intended dimensions/page size and background treatment, and contains the expected raster or vector content before delivery.
