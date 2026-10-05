# Engine `html`: HTML/SVG rendered to PNG

Claude writes the diagram as one HTML file with the design tokens and the self-hosted Poppins. A headless
Edge / Chrome renders it. Costs no credits, text and diacritics are always exact, colors are exact
tokens (no post-processing), and the same source renders in every theme and language.

## 1. Write the source

Start from the closest file in `assets/examples/` (or a blank skeleton below) and save the copy in the
**scratchpad**, never in the repo:

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<!-- What this diagram shows, in one line. -->
<link rel="stylesheet" href="base.css">
<style>
  /* layout for this diagram only: grid / flex, sizes in px for a 1200 px canvas, colors only var(--d-*) */
</style>
</head>
<body>
<script src="diagram.js"></script>
<div class="diagram">
  …
</div>
</body>
</html>
```

- `base.css` and `diagram.js` are linked by bare name: the render script copies them (and `fonts/`)
  next to the HTML. Don't change the paths.
- **Languages in one file:** every label is a pair `<span data-l="en">Why now</span><span data-l="sk">Prečo teraz</span>`.
  The script renders each language with `?lang=…`, so both versions are structurally identical by
  construction. A single-language entry may use plain text and no `--lang`.
- Colors only through `var(--d-*)` (patterns.md §2), and categories through `data-cat` + `.cat-fill` /
  `.cat-line` / `.cat-text` / `.cat-dot`. No hex, no `rgba()` of your own.
- Sizes: text classes only (`.h`, `.label`, `.text`, `.eyebrow`); don't set a font size below
  `var(--fs-text)`. Strokes `var(--stroke)` (3 px) for outlines, `var(--hair)` (2 px) for hairlines.
- Geometry (circles, lenses, arcs, arrows, curved connectors) as inline SVG with `stroke` / `fill` set
  in the `<style>` block via `var(--d-*)`. Put text as HTML over the SVG (absolute positioning) so it
  uses Poppins and wraps; compute positions from the SVG coordinates (see `venn.html`).
- Arrows on curves (cycles, loops): draw each segment as an arc `<path>` between two nodes and give it
  an SVG `<marker>` arrowhead (`marker-end`), so the head follows the curve. Hand-placed chevrons near a
  curve never quite sit on it.
- `text-wrap: balance` is on by default for text classes; break lines by layout width, not with `<br>`.
- Grid gotcha: `grid-row: 2 / -1` doesn't reach the last row in an implicit grid. Use
  `grid-row: 2 / span N` (see `swimlane.html`).

### Lines (connectors): let `diagram.js` draw them

Never build connectors from borders, pseudo-elements or hand-placed SVG coordinates: they end up off by
a few pixels, with hard corners. Declare them and `diagram.js` measures the laid-out elements (after the
fonts loaded) and draws smooth SVG paths with rounded corners and round caps, behind the content.

```html
<!-- one connector: give both ends an id -->
<i class="link" data-from="root" data-to="menu" data-shape="elbow" data-radius="22"></i>
<i class="link" data-from="doc" data-to="table" data-shape="straight" data-from-side="right" data-to-side="left"
   data-tone="accent" data-weight="stroke" data-arrow="end" data-gap="28"></i>
<!-- a whole tree: every direct child of the container gets ├ └ from the parent -->
<div class="kids" data-tree-from="p-approach" data-inset="12" data-gap="10">…</div>
```

| Attribute | Values (default) |
|---|---|
| `data-shape` | `elbow` (orthogonal, rounded corners: buses, org charts), `tree` (spine + rounded turn into each child's left side), `curve` (smooth S-curve), `straight` (side to side it runs level through the elements' overlap), `radial` (center to center, trimmed exactly at both outlines: circles, pills, boxes; spider and hub diagrams) |
| `data-from-side` / `data-to-side` | `top`, `bottom`, `left`, `right` (picked from the layout: a target fully below goes bottom → top) |
| `data-mid` | elbow: where the cross segment runs, 0–1 (`.5`) |
| `data-radius` | corner radius px (`16`; trees `14`) |
| `data-inset` | tree: spine distance from the parent's left edge (`24`) |
| `data-gap` | free px before the target (`0`; `10` with an arrow) |
| `data-tone` | `line` (hairline gray), `outline` (text color), `accent` |
| `data-weight` | `hair` (2 px), `stroke` (3 px) |
| `data-arrow` | `end`, `start`, `both` (open chevron, round joins) |

Siblings that share a source and the same target row share the trunk automatically (same mid line),
which gives the clean bus of `uml-types.html` and `sitemap.html`.

## 2. Craft: make it look designed, not like a screenshot of HTML

Before rendering, and again when looking at the result, go through this list. The bar is
`assets/references/` (approved diagrams); the target is that a designer would have drawn it.

- **Reference first.** Pick the closest image in `assets/references/` (or the user's reference, SKILL.md
  Step 5) and name what to take from it: grid, density, connector style, proportions.
- **Lines:** all connectors through `diagram.js`; rounded corners (radius 14–24), round caps; one
  weight per role (2 px connectors, 3 px outlines and arrows); lines stop a consistent gap before
  their target; no line crosses text.
- **Rhythm:** one spacing scale (8 / 16 / 24 / 32 / 48 px) used consistently; equal gaps between
  siblings; repeated elements (bars, rows, pills) identical in height and spacing.
- **Alignment:** a shared grid (subgrid for table-like rows); headings in a row on one baseline;
  columns of bars line up with their labels.
- **Balance:** the canvas is filled evenly, no big empty corner (move a legend or note into it, or
  change the column split); the focal element sits where the eye lands first.
- **Abstract stand-ins** (bars for text, rows for data) are dense and even, like the document in
  `two-outputs.png`, not a few random lines.
- **Shapes:** one radius family (pills 999, boxes 24, inner boxes 20); outlines either 2 or 3 px, never
  mixed within a group.
- **Type:** no orphans, no single word on a line, headings never wrap into 3+ lines (give them a wider
  cell or a shared header row); paths and codes `nowrap`.
- **Legend:** shows a swatch, not a repeated label.

## 3. Render

```
python scripts/render_diagram.py <scratch>/<name>.html --out-dir <scratch>/out --name <name> --lang en,sk [--theme dark]
```

| Option | Default | |
|---|---|---|
| `--lang` | none | comma list, one PNG per language: `<name>-<lang>.png` |
| `--theme` | `dark` | `dark`, `dark-subtle`, `light`, `primary`, `brand` |
| `--colors` | `mono` | `palette` turns on the decorative category colors declared with `data-cat` (themes.md → Decorative colors). Decide per `colors=auto` rules; the same source renders both. |
| `--variant` | none | file suffix for extra versions: `--variant light` → `<name>-<lang>-light.png` |
| `--bg` / `--accent` / `--on-accent` / `--light` | | brand / custom surface (`--theme brand` needs `--bg`) |
| `--width` | `1920` | output width; the canvas is 1200 CSS px, rendered at width/1200 device scale |

What the script does:
- Finds Edge or Chrome (Windows Program Files, macOS Applications, Linux `PATH`; override with
  `DIAGRAM_BROWSER=<path>`). Nothing is installed.
- Renders in a temp folder with the assets copied next to the HTML, crops to the `.diagram` canvas (the
  page around it is a magenta sentinel), retries with a taller window if the canvas touched the bottom.
- Checks that all four corners are exactly the theme background (`bg_ok`).
- Saves an optimized PNG with the source HTML and render params embedded (iTXt chunk
  `content-diagrams:source`), and a phone-size preview `previews/<file>-358.png`.
- Last stdout line = JSON report (`size`, `ratio`, `kb`, `bg_measured`, `bg_ok`); exit 1 on a failed
  render or a background mismatch.

If Poppins fails to load, `diagram.js` puts a red **FONT FAILED TO LOAD** banner on the image: the
Step 7 visual check can't miss it.

## 4. Edit later

```
python scripts/render_diagram.py --extract <file.png> -o <scratch>/<name>.html
```

Writes the byte-exact source back out (and prints the params it was rendered with). Edit, render again.
A PNG made by Higgsfield has no source; it can only be regenerated.

## 5. Verify (in addition to SKILL.md Step 7)

- Look at every PNG **and** its 358 px preview.
- `bg_ok: true` for each file.
- Ratio between 16:9 (1.78) and 3:4 (0.75). Outside → restructure (stack, split) instead of shipping.
- Nothing overflows the canvas or overlaps; no orphaned single word on a line if a wider column fixes it.
