# Engine `higgsfield`: image model + post-processing

**Only on request.** The default is the html engine, because the design system's font is Poppins and
no image model renders Poppins: the best one draws a Poppins-like geometric sans. Say so when the user
asks for Higgsfield.

The route of the reference run (UX-audit article): the model draws the diagram from a text prompt, a
script snaps the background to the exact token. Costs credits (1 per image at 3:4, ~1.5 at 16:9), and
every label must be checked letter by letter.

## 1. Prompt

Fixed style block: fill `{…}` from the theme (themes.md), keep the rest verbatim.

```text
Flat minimal infographic diagram for {a blog article | a web page section}, clean product-design style.
STYLE RULES: Background solid flat {BG_HEX} ({BG_DESC}), full bleed to every edge, no border,
no frame. Typography: clean geometric sans-serif like Poppins; headings and labels in medium weight,
supporting text in regular weight; primary labels {TEXT_HEX}, secondary labels {SUBTLE_HEX}.
Single accent color {ACCENT_HEX} ({ACCENT_DESC}), used sparingly{ACCENT_RULE}. Shapes: pill-shaped and
rounded-rectangle elements, thin 2px lines in {LINE_HEX}, flat fills only. No gradients, no shadows,
no 3D, no textures, no icons, no logos, no watermark. Generous whitespace, precise alignment.
LARGE TEXT, FEW ELEMENTS: the image must stay readable when shown 360 px wide on a phone, so the
smallest text is at least 1/35 of the image width and there are at most about 12 labels.
Render ALL text exactly as written below, correctly spelled, and add NO other text, words or numbers.

CONTENT: {"Slovak language, correctly spelled with Slovak diacritics." for SK} {layout description; every label in "quotes"}
```

| Theme | `BG_HEX` | `TEXT_HEX` | `SUBTLE_HEX` | `LINE_HEX` | `ACCENT_HEX` | `{ACCENT_RULE}` |
|---|---|---|---|---|---|---|
| dark | `#312F3D` (dark graphite) | `#F4F3F6` | `#787292` | `#605B76` | `#F5A816` (warm amber) | empty |
| dark-subtle | `#494559` | `#F4F3F6` | `#AFABBF` | `#787292` | `#F5A816` | empty |
| light | `#F4F3F6` (very light cool gray) | `#1F1D26` | `#605B76` | `#CBC8D5` | `#F5A816` | ", only as solid fills with dark text, never as thin outlines or small text" |
| primary | `#F5A816` (warm amber) | `#1F1D26` | `#312F3D` | `#312F3D` | replace the whole accent sentence with: "Accent: solid #1F1D26 fills with #F4F3F6 text." | |
| brand | `brand.surface` | per themes.md | | | `brand.primary` | |

- `CONTENT`: describe the layout you designed (patterns.md §1, §3) in plain words, every label in
  "quotes". The approved descriptions are in patterns.md §5.
- **Slovak:** spell out very short or tricky labels. "Čo" once came out as "Č čo"; the retry that worked
  said `the single two-letter word "Čo" (capital C with caron, then o)`.
- Both language versions: the same layout text, only the labels differ.

## 2. Model

**Use `gpt_image_2_5`, `variant: sunburst`, `quality: medium`, `resolution: 2k`** (1 credit at 3:4).
The user picked sunburst after the side-by-side test: cleaner connector lines, bigger text, a font that
looks right next to the site. Its font is still not Poppins; say so when the user asks for Higgsfield.

- **Fallback `variant: flare`** (leave `variant` unset): the retry when sunburst gets text wrong
  (that is the one allowed retry), or when the user wants the font closest to Poppins.
- Don't leave the choice to Higgsfield: no `variant` means flare, and `image_auto` picks a model
  unpredictably.
- No other models without the user asking. Text wrong twice → switch to the html engine.

Tested on 2026-10-05 with the same prompt (meetbrackets.com sitemap, SK, 37 labels with diacritics, 3:4):

| Model | Credits / image | Result |
|---|---|---|
| `gpt_image_2_5` `variant: flare` (default when unset), medium 2k | 1 (3:4; ~1.5 at 16:9) | All 37 labels correct, layout as described. Font closest to Poppins (narrower, heavier headings, different a / y); ignores the "large text" rule (text ~half the size of the html engine, small on a phone). **Fallback.** |
| **`gpt_image_2_5` `variant: sunburst`**, medium 2k | **1** via the API (the Higgsfield web UI may price it higher) | **All labels correct**, text bigger than flare, clean tree connectors (├ └) it added itself. Font Inter / Google Sans-like, not Poppins, but the user preferred its look. **Default.** |
| `nano_banana_pro` 2k (Google) | 2 | **All 37 labels correct**, layout as described, text size close to the "large text" rule (readable on a phone, like the html engine). **Rejected: the font is a neutral grotesque (Inter-like), not Poppins.** |
| `nano_banana_2` 2k | 2 | Fail: text correct, but it invented outlined pills around the headings that cut through the paths. |
| `ideogram_4_5` medium 2k, `magic_prompt: off` | 2 | Fail: structure scrambled, labels duplicated and moved, misspellings ("ROI Culator", "/0 člálkov"). |
| `openai_hazel` medium | 4 | Fail, despite its "best text rendering / diagram" tags: garbled text, glow and gradient, wrong background, only 1024 px wide. |
| `recraft_v4_1` | 8 at 2k | Not tested (price). Has `colors` / `background_color` controls; a candidate only if gpt_image_2_5 fails on a diagram. |
| `gpt_image_2_5` high | ~2.75 | Not needed for flat diagrams. |

Flare renders text smaller than asked (sunburst less so), so keep Higgsfield diagrams to fewer labels than the
html engine would hold, and check the 358 px preview.

## 3. Generate

- Check `balance` first.
- `generate_image_batch` with every diagram × language × theme: `model: gpt_image_2_5`,
  `variant: sunburst`, `quality: medium`, `resolution: 2k`, `aspect_ratio: 4:3` (also `16:9`, `3:2`, `1:1`, `3:4` when the
  layout needs it), no reference image.
- `jobs_wait` until all are terminal.
- Expect partial failures (`429 rate_limit_reached`, 4 of 8 in the reference run; `503`). Resubmit
  **only the failed indices** in a smaller batch. Never resubmit the whole batch: duplicates cost credits.
- Download each result into the scratchpad (`curl -L -o <scratch>/raw/<file>.png <url>`).
- Check `balance` again; report the credits spent.

## 4. Post-process

```
python scripts/postprocess_diagram.py <scratch>/raw/<file>.png <scratch>/out/<file>.png --bg "#312F3D" [--crop]
```

- Measures the background, shifts all channels by target − measured (on dark themes; `--no-shift` is the
  default on light backgrounds, where the shift wasn't tested and could drift dark text), snaps
  near-background pixels to the exact hex, optional `--crop` to content + 140 px (wide timelines),
  resizes to 1920 px, saves an optimized PNG. JSON report with `bg_ok`.
- Windows: pass `C:/Users/…` paths, not Git-Bash `/c/Users/…`.
- A Higgsfield PNG has no editable source: changes mean a new generation.

## 5. Verify (in addition to SKILL.md Step 7)

- Every label letter by letter, including diacritics. No extra text, no invented numbers.
- Layout matches the description; nothing invented.
- Make a 358 px preview yourself (Pillow resize) and look at it.
- Accent fills may show slight noise; that's the model, not the post-process. Mention it if visible.
- A failure (wrong text, extra elements) gets one regeneration of that image only. Fails again → report.
