---
name: ai-disclosure
description: Burn the official EU AI-disclosure icon ("AI", "AI GENERATED", "AI MODIFIED") directly into an image file as a visible watermark, after the image has been generated or edited. Classifies the image first (illustration, diagram, UI mockup, photorealistic, AI-edited real photo) to decide whether a label is needed and which one, or applies the label the user names. Use it right after /article-illustration or any Higgsfield / image-model generation, and whenever the user says "AI disclosure", "AI label", "AI vodotlač", "AI watermark", "označ ako AI", "pridaj AI ikonu", "AI generated badge", or asks whether an image must be labelled under the AI Act.
argument-hint: "<image path(s)> [label=auto|ai|generated|modified] [corner=auto|br|bl|tr|tl]"
---

# /ai-disclosure

Put the EU AI-disclosure icon **into the pixels** of an image, so the label survives downloading,
re-sharing and cropping on other platforms. No HTML overlay, no template change.

## Usage

```
/ai-disclosure <image path | folder> [label=auto] [corner=auto] [style=solid]
```

Input: @$1

| Option | Default | Notes |
|---|---|---|
| `label` | `auto` | `auto` = classify first (Step 2). Or force `ai`, `generated`, `modified`. |
| `corner` | `auto` | Bottom-right unless that corner sits on detail; then the calmest corner. |
| `tone` | `auto` | White pill on dark areas, black pill on light areas. |
| `style` | `solid` | `transparent` = official 50 % variant. Solid is more legible; keep it unless asked. |

If the user says "just add it" / "pridaj tam AI vodotlač" without naming a label, skip the legal
question and treat it as `label=auto` **with apply forced** (Step 2 picks the variant, but never
decides "skip").

## How It Works

```
1. Resolve input      → image path(s); ask only if none given
2. Classify           → category + label + required / voluntary / skip
3. Analyze            → scripts/apply_disclosure.py --analyze (corner, tone, size)
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

## Step 2 — Classify (skip if the user forced a label)

**Look at the image.** Decide the category from what it shows, plus what you know about how it was
made (a generation in this session, the user's description, file name). Then read the row in
`references/classification.md` for the reasoning; the short version:

| Category | Looks like | Label | Status |
|---|---|---|---|
| Stylized illustration | risograph / pop-art, drawn, clearly not a photo | `generated` | Voluntary (BRACKETS policy: label it) |
| Diagram / infographic | boxes, arrows, charts, schematic | none | Skip, not required |
| UI mockup, fictional product | app/web screens that don't claim to be a real product | none | Skip, not required |
| UI mockup presented as a real product / client screen | looks like a real screenshot of something that doesn't exist that way | `generated` | Required (borderline, label it) |
| Photorealistic, fully generated | people, offices, places, events, objects that look real | `generated` | **Required** |
| Real photo edited by AI | real team / office photo with replaced background, added or removed elements | `modified` | **Required** if the edit could pass as authentic |
| Any category, small format | shorter side < 500 px (thumbnail, avatar, square social crop) | `ai` | Same as above, compact icon |

Rules:
- When unsure between illustration and photorealistic, treat it as photorealistic.
- When unsure whether AI was involved at all, **ask**. Don't label human-made work.
- "Skip" means: tell the user it isn't required and that you can still add it in one step.
  Don't apply it silently.

## Step 3 — Analyze

```bash
python3 <skill>/scripts/apply_disclosure.py <image> --label <label> --analyze
```

Returns image size, icon size, per-corner luminance and busyness (std-dev of luminance, 0 = flat
color), `suggested_corner`, `suggested_tone`, `small_format`. If `small_format` is true and the label
is `generated` or `modified`, switch to `ai`.

## Step 4 — Burn in

```bash
python3 <skill>/scripts/apply_disclosure.py <image> --label <label> [--corner br] [--tone auto]
```

- Writes `<name>-ai.<ext>` next to the input. **The original is never overwritten by default.**
  `--overwrite` exists, but only use it after Step 6 confirmation.
- Needs only Pillow (`pip install pillow`). Icons are pre-rendered PNGs in `assets/icons/`
  (official EU SVGs in `assets/svg/` are the source of truth).
- Size: pill height 4 % of the shorter side, round `AI` badge 7 %, margin 3 %. On a 2000×1116 cover
  that is a 233×45 px pill, 33 px from the edge. Override with `--scale` / `--margin` only when asked.
- Also writes XMP `Iptc4xmpExt:DigitalSourceType` (`trainedAlgorithmicMedia` or
  `compositeWithTrainedAlgorithmicMedia`), so the file carries a machine-readable flag too.
- Re-encoding changes the pixels, so any C2PA manifest from the generator (Higgsfield) no longer
  validates. That is expected. The visible icon plus the XMP flag replace it.

## Step 5 — Verify

View the output. Check:
- The icon is legible (contrast against what's under it) and fully inside the canvas.
- It doesn't cover the focal element, a face, or anything important. If it does, rerun with another
  `--corner`.
- Crops: for /thinking covers the site crops responsively. The 3 % margin keeps the icon out of the
  outermost edge, but if you know a tighter crop is used (e.g. 4:5 card), mention it.

## Step 6 — Hand-off

1. Show the result and the chosen label.
2. Offer alt text with the disclosure, bilingual:
   - EN: `{description}. Illustration generated with AI.` / `… edited with AI.`
   - SK: `{popis}. Ilustrácia vytvorená pomocou AI.` / `… upravená pomocou AI.`
3. For meetbrackets.com: the final file replaces
   `src/assets/images/thinking/<slug>/featuredMedia/image.jpg`. Ask before replacing. If the entry
   schema has an `aiDisclosure` field, set it (`generated` / `modified`); if not, just mention it.

## Output

```markdown
Hotovo: `{output path}`

**Klasifikácia:** {category} → `{label}` ({povinné / dobrovoľné})
**Umiestnenie:** {corner}, {tone} pill, {w}×{h} px

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
