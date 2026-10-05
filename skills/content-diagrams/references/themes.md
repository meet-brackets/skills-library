# Themes: token sets per surface

A diagram must look like it was drawn on the section it sits in. Every theme uses **only** brackets-web
design tokens. Source of truth: brackets-web `src/styles/tokens/colors.css` and `theme.css`. When those
change, update this file **and** `assets/base.css` (same values, `[data-theme]` blocks).

The web's "white" is `--color-white` = gray-50 **`#F4F3F6`**, not `#FFFFFF`. The web's "black" is
gray-900 `#1F1D26`.

| Role → | Background | Primary text, outlines | Secondary text | Hairlines, quiet outlines | Accent (fills) | Text on accent | Thin accent lines, numbers |
|---|---|---|---|---|---|---|---|
| **dark** (default, `surface-inverse`) | `#312F3D` gray-800 | `#F4F3F6` gray-50 | `#787292` gray-500 | `#605B76` gray-600 | `#F5A816` Supernova | `#1F1D26` | `#F5A816` |
| **dark-subtle** (`surface-inverse-subtle`) | `#494559` gray-700 | `#F4F3F6` | `#AFABBF` gray-300 | `#787292` gray-500 | `#F5A816` | `#1F1D26` | `#F5A816` |
| **light** (`surface`) | `#F4F3F6` gray-50 | `#1F1D26` gray-900 | `#605B76` gray-600 | `#CBC8D5` gray-200 | `#F5A816` (fills only) | `#1F1D26` | `#1F1D26` |
| **primary** (`primary`) | `#F5A816` Supernova | `#1F1D26` | `#312F3D` gray-800 | `#312F3D` | `#1F1D26` gray-900 | `#F4F3F6` | `#1F1D26` |
| **brand** (case study) | `brand.surface` | gray-50, or gray-900 with `lightSurface` | gray-300 / gray-600 | gray-500 / gray-600 | `brand.primary` | per contrast | `brand.primary` |

Token names behind the columns: background `--bg-surface*`; text `--text-color` / `--text-inverse`;
secondary `--text-subtle` / `--text-inverse-subtle`; hairlines `--border-color` / `--border-inverse`;
outlines `--border-strong` / `--border-inverse-strong`; accent `--color-primary`.

## Rules per theme

- **dark-subtle:** secondary text is gray-300, not gray-500 (gray-500 is too close to gray-700).
- **light:** Supernova has low contrast on `#F4F3F6`. Use it only as a **fill** (with gray-900 text) or
  for thick shapes. Thin accent outlines, accent numbers and accent text become gray-900. `base.css`
  does this through `--d-accent-line`.
- **primary:** the yellow can't accent itself. Accent = gray-900 fills with gray-50 text. No other colors.
- **brand:** only when the content really renders on the case study's brand surface
  (`CaseStudyDetail.astro` sets `--cs-surface` from `brand.surface`), or when the user asks. Colors come
  from the case study frontmatter `brand` (`primary`, `surface`, `lightSurface`), which comes from the
  Figma "Website: Brand" collection (brackets-web `.claude/rules/case-study-guide.md`). HTML engine:
  `--theme brand --bg <surface> --accent <primary> [--light]`, plus `--on-accent` when the accent is
  dark.
- **custom** ("na žltom", "na bielom", a hex): snap to the nearest token surface above and say so in
  one line ("na žltom" → primary, "na bielom" → light). A hex that is no token → nearest theme by
  luminance, never an off-system color.

## Status colors (optional)

Only when the diagram encodes a status or level, same mapping as the site's `{% status %}` pill:
low = Success `#34D399` (Carribean Green), medium = Warning `#F97316` (Crusta), high = Danger
`#F43F5E` (Radical Red). Small dots or pill dots only (`.dot.low|medium|high`), never backgrounds,
never large areas.

## Decorative colors (option `colors`)

The web design system's decorative palette (brackets-web `colors.css`, Figma "Decorative colors").
**Default `colors=auto` keeps diagrams monochrome:** the theme grays plus the one accent. Decorative
colors come in only when the content needs them to tell categories apart:

| Mode | When |
|---|---|
| `auto` (default) | Monochrome, unless the diagram has **3+ categories the reader must tell apart** (a legend, data series, layers or teams that recur across the diagram, a color-coded map). Then one decorative color per category. Two groups or a single highlight never need colors: use the accent, outline vs. fill, or position. Say in one line when auto added colors and why. |
| `mono` | Never decorative colors. |
| `palette` | The user asked for it ("sprav to farebnejšie", "viac farieb", "colorful"): give each category or group its own color, still by the rules below. |

| Order | Name | Hex | Text on its fill | As thin line / dot / text on dark | … on light |
|---|---|---|---|---|---|
| 1 | Cornflower Blue | `#2563EB` | gray-50 | no (2.5:1) | yes |
| 2 | Princess Perfume | `#DB2777` | gray-50 | no (2.9:1) | yes |
| 3 | Keppel | `#14B8A6` | gray-900 | yes | no (2.3:1) |
| 4 | Biloba Flower | `#9333EA` | gray-50 | no (2.4:1) | yes |
| 5 | Crusta | `#F97316` | gray-900 | yes | no (2.5:1) |
| 6 | Deep Sky | `#22D3EE` | gray-900 | yes | no (1.6:1) |
| 7 | Blue Violet | `#4F46E5` | gray-50 | no (2.1:1) | yes |
| 8 | Carribean Green | `#34D399` | gray-900 | yes | no (1.7:1) |
| 9 | Radical Red | `#F43F5E` | gray-900 | yes | yes |

Rules:
- **Meaning, not decoration.** A color = a category, the same category keeps its color everywhere in
  the diagram (and across the article's diagrams). Add a legend unless the labels already name the
  categories.
- Take colors **in the order above** (chosen to stay distinguishable); at most 5 in one diagram.
  Supernova is not in the list: it stays the single focal accent.
- **Fills** (boxes, pills, header bars, tiles) work with any color on any theme, with the text color
  from the table (`.cat-fill` sets it). **Thin lines, dots and text** only where the table says yes for
  that theme; otherwise use a fill.
- Carribean Green, Crusta and Radical Red also mean low / medium / high status. In a diagram that shows
  status, don't use them for categories.
- Primary theme (Supernova surface): decorative colors only as fills with their own text color, never
  next to large Supernova areas without a gray-900 separation.
- HTML engine: `data-cat="cornflower-blue"` on an element + `.cat-fill` / `.cat-line` / `.cat-text` /
  `.cat-dot` (`assets/base.css`). Higgsfield: name the hexes in the prompt and verify them.

## Typography (brackets-web `typography.css`, `text-styles.css`)

- Poppins (`--font-sans`): headings and labels medium 500, supporting text regular 400. 600 exists for
  rare emphasis; never 700 (the site doesn't load it).
- JetBrains Mono (`--font-mono`): optional eyebrow / column headers, as on article tables.
- Max 3 levels in one diagram: heading → label → supporting text.
