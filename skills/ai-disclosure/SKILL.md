---
name: ai-disclosure
description: Burn the official EU AI-disclosure icon (the basic "AI" icon by default; "AI GENERATED" / "AI MODIFIED" on request) directly into an image file as a subtle visible watermark, after the image has been generated or edited. Classifies the image first (illustration, diagram, UI mockup, photorealistic, AI-edited real photo) to decide whether a label is needed and whether it's generated or modified, or applies the label the user names. Use it right after /article-illustration or any Higgsfield / image-model generation, and whenever the user says "AI disclosure", "AI label", "AI vodotlač", "AI watermark", "označ ako AI", "pridaj AI ikonu", "AI generated badge", or asks whether an image must be labelled under the AI Act.
argument-hint: "<image path(s)> [label=ai|generated|modified] [source=auto|generated|modified] [corner=auto|br|bl|tr|tl]"
---

# /ai-disclosure

Put the EU AI-disclosure icon **into the pixels** of an image, so the label survives downloading,
re-sharing and cropping on other platforms. No HTML overlay, no template change.

## Usage

```
/ai-disclosure <image path | folder> [label=ai] [source=auto] [corner=auto] [style=auto]
```

Input: @$1

| Option | Default | Notes |
|---|---|---|
| `label` | `ai` | Visible icon. `ai` = basic EU icon, no text. `generated` / `modified` = text pills, only when the user asks for them. |
| `source` | `auto` | What metadata and alt text say: `generated` or `modified`. `auto` = from Step 2 (or from a text `label`). |
| `corner` | `auto` | Bottom-right unless that corner sits on detail; then the calmest corner. |
| `style` | `auto` | Official 50 % transparent variant on a calm corner, solid on a busy one (the icon must stay visible against any background). Force `solid` / `transparent` only when asked. |
| `tone` | `auto` | The variant whose contrast holds on that corner: solid = the disc contrasts with the background, transparent = the letters do. |

If the user says "just add it" / "pridaj tam AI vodotlač" without naming a label, skip the legal
question and apply it: Step 2 still picks the `source` for metadata and alt text, but never decides
"skip".

## How It Works

```
1. Resolve input      → image path(s); ask only if none given
2. Classify           → category + source + required / voluntary / skip
3. Analyze            → scripts/apply_disclosure.py --analyze (corner, style, tone, size)
4. Burn in            → scripts/apply_disclosure.py → <name>-ai.<ext>  (original untouched)
5. Verify             → look at the result, check legibility and what it covers
6. Hand-off           → alt text, frontmatter flag, replace original only after OK
```

## Step 1 — Resolve input

- A path, several paths or a folder (process every `.jpg/.jpeg/.png/.webp` in it).
- Right after `/article-illustration` in the same session: use the downloaded variant(s) the user
  picked. In a new session: ask for the path, or look in
  `src/assets/images/thinking/<slug>/featuredMedia/` if the user names the article.
- Video (`.mp4` etc.) is out of scope for this version. Say so in one line.

## Step 2 — Classify (skip if the user named the source or a text label)

**Look at the image.** Decide the category from what it shows, plus what you know about how it was
made (a generation in this session, the user's description, file name). Then read the row in
`references/classification.md` for the reasoning. The visible icon is the basic `AI` icon in every
row. The category only decides whether it goes on at all, and which `source` the metadata and alt
text state:

| Category | Looks like | Source | Status |
|---|---|---|---|
| Stylized illustration | risograph / pop-art, drawn, clearly not a photo | `generated` | Voluntary (BRACKETS policy: label it) |
| Diagram / infographic | boxes, arrows, charts, schematic | none | Skip, not required |
| UI mockup, fictional product | app/web screens that don't claim to be a real product | none | Skip, not required |
| UI mockup presented as a real product / client screen | looks like a real screenshot of something that doesn't exist that way | `generated` | Required (borderline, label it) |
| Photorealistic, fully generated | people, offices, places, events, objects that look real | `generated` | **Required** |
| Real photo edited by AI | real team / office photo with replaced background, added or removed elements | `modified` | **Required** if the edit could pass as authentic |

Rules:
- When unsure between illustration and photorealistic, treat it as photorealistic.
- When unsure whether AI was involved at all, **ask**. Don't label human-made work.
- "Skip" means: tell the user it isn't required and that you can still add it in one step.
  Don't apply it silently.
- Text pills (`AI GENERATED` / `AI MODIFIED`) only when the user asks for them. The EU Code of
  Practice requires only the `AI` acronym (Measure 1.1(a)); the text is encouraged, not required
  (Measure 1.1(b)).
- For a photorealistic deep fake of a real, identifiable person or a news-like event, say in one
  sentence that the EU recommends the text variant there (clearer in user testing). Keep `ai` unless
  the user switches.

## Step 3 — Analyze

```bash
python3 <skill>/scripts/apply_disclosure.py <image> --analyze
```

Returns image size, icon size, per-corner luminance and busyness (std-dev of luminance, 0 = flat
color), `suggested_corner`, `suggested_style`, `suggested_tone`, and `small_format` (info only).

## Step 4 — Burn in

```bash
python3 <skill>/scripts/apply_disclosure.py <image> --source <generated|modified> [--corner br]
```

- Writes `<name>-ai.<ext>` next to the input. **The original is never overwritten by default.**
  `--overwrite` exists, but only use it after Step 6 confirmation.
- Needs only Pillow (`pip install pillow`). Icons are pre-rendered PNGs in `assets/icons/`
  (official EU SVGs in `assets/svg/` are the source of truth).
- Size: icon height 4 % of the shorter side (min 24 px), the same for the badge and the pills;
  margin 3 %. On 1920×1080 that is a 43 px `AI` badge, 32 px from the edge; on a 2000×1116 cover
  45 px, 33 px. There is no legal minimum; what counts is legibility at the size the image is
  displayed (`references/classification.md` → Size). Override with `--scale` / `--margin` only when
  asked.
- Also writes XMP `Iptc4xmpExt:DigitalSourceType` from `--source` (`trainedAlgorithmicMedia` or
  `compositeWithTrainedAlgorithmicMedia`), so the file carries a machine-readable flag too.
- Applies the EXIF orientation first, so on phone photos the icon lands in the corner people see.
- Re-encoding changes the pixels, so any C2PA manifest from the generator (Higgsfield) no longer
  validates. That is expected. The visible icon plus the XMP flag replace it.

## Step 5 — Verify

View the output. Check:
- The icon is legible (contrast against what's under it) and fully inside the canvas.
- With the transparent variant, the letters must still read clearly. If they don't, rerun with
  `--style solid`.
- It doesn't cover the focal element, a face, or anything important. If it does, rerun with another
  `--corner`.
- Crops: for /thinking covers the site crops responsively. The 3 % margin keeps the icon out of the
  outermost edge, but if you know a tighter crop is used (e.g. 4:5 card), mention it.

## Step 6 — Hand-off

1. Show the result, the category and the source.
2. Always offer alt text with the disclosure, bilingual. It carries the generated / edited detail the
   basic icon doesn't show, and Art. 50(5) requires the disclosure to be accessible:
   - EN: `{description}. Illustration generated with AI.` / `… edited with AI.`
   - SK: `{popis}. Ilustrácia vytvorená pomocou AI.` / `… upravená pomocou AI.`
3. For meetbrackets.com: the final file replaces
   `src/assets/images/thinking/<slug>/featuredMedia/image.jpg`. Ask before replacing. If the entry
   schema has an `aiDisclosure` field, set it to the source (`generated` / `modified`); if not, just
   mention it.

## Output

```markdown
Hotovo: `{output path}`

**Klasifikácia:** {category} → {generated / modified} ({povinné / dobrovoľné})
**Ikona:** `{label}`, {style}, {tone}, {w}×{h} px, {corner}

Alt text:
- EN: `{…}`
- SK: `{…}`

{one question: replace the original / move the icon / use another label}
```

For "skip" results:

```markdown
`{file}` je {category}. AI označenie tu povinné nie je ({one-line reason}).
Mám ho aj tak pridať?
```

Reply in the user's language (template is Slovak, the BRACKETS default). Labels on the icon stay in
English on every language version of the site. They're the official EU icons and aren't translated.

## Tips

1. Using this after `/article-illustration`: run it only on the variant the user picked, not on every
   variant.
2. Batch: for a folder, classify each image separately. Don't assume one category for all.
3. Never redraw, recolor, stretch or crop the EU icon. Only scale it proportionally
   (the script does this).
4. The EU icons are free to use without attribution. Using them isn't a claim that BRACKETS signed
   the EU Code of Practice.
