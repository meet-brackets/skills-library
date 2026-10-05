# Diagram types and composition

**The diagram follows the content, not a menu.** Start from the shape of the idea in the text, then pick
or invent the form that shows it most directly. The examples in `assets/examples/` are style references
(how BRACKETS diagrams look and how the building blocks combine), **not** a closed set of templates.
Reuse their CSS where it fits; otherwise build a new layout from the same blocks.

## 1. Find the shape of the content

Write the point of the section in one sentence, then ask what relationship it describes:

| The content is about… | Forms that show it | Notes |
|---|---|---|
| Steps in order | numbered flow, timeline (vertical for 5+ steps), stepper with branches | Branch only where the text branches. |
| A repeating loop | cycle (3–6 nodes on a circle or rounded track) | Mark the start. Arrows show direction. |
| Narrowing / filtering | funnel, stacked bars getting shorter | Numbers only if the text gives them. |
| Levels, layers, foundations | stack, pyramid, nested boxes | Bottom = foundation, unless the text says otherwise. |
| Parts of a whole / hierarchy | tree, org chart, nested groups | Max 3 levels. |
| A website or app structure | sitemap: root on top, a bus into 2 columns of groups, pages with paths, children as a hairline list | Real paths and counts from the repo, never guessed. |
| Something central with satellites | hub and spoke, spider / mind map (`spider.html`) | The hub carries the accent; branches by quadrant, leaves point outwards. |
| Overlap of two or three views | Venn | Overlap filled with the accent. |
| Two criteria | 2×2 matrix | The best quadrant filled. Axis ends labelled. |
| One dimension / trade-off | spectrum, scale, slider with marked positions | Ends labelled, positions as pills or dots. |
| Bad vs good, before vs after, A vs B | two-panel comparison, split | Same structure on both sides so the difference stands out. |
| Choices depending on conditions | decision tree, "if → then" rows | Questions as text, outcomes as pills. |
| Items × moments / roles × tasks | swimlane, mapping grid with dots | A cell that is the same on both sides = one spanning element. |
| A journey with stages | horizontal stages + one row per aspect | Keep to 3–5 stages. |
| Quantities the text actually states | simple bar / proportion / big-number tiles | Real numbers only, never invented. Follow the `dataviz` skill for charts with axes. |
| A checklist or a set of criteria | grid of pills, grouped list | Only if it adds structure; otherwise keep it as text. |

If no form fits, the content probably doesn't need a diagram: say so and leave it as text or as the
one allowed table (SKILL.md Step 2).

## 2. Building blocks (`assets/base.css`)

| Class | What it is |
|---|---|
| `.diagram` | the canvas: 1200 CSS px wide, 4:3 by default (`.ratio-16-9`, `.ratio-3-2`, `.ratio-1-1`, `.ratio-auto`), padding 80 px |
| `.h` / `.label` / `.text` / `.eyebrow` | heading 56 / label 44 / supporting text 34 (the minimum) / mono eyebrow 34 |
| `.pill` (+ `.small`, `.quiet`, `.accent`, `.fill`) | rounded pill: outline in text color, quiet hairline, accent outline, accent fill |
| `.box` (+ `.strong`, `.fill`) | rounded rectangle (radius 24): hairline, strong outline, accent fill |
| `.num` (+ `.fill`) | numbered circle 96 px, accent outline or fill |
| `.hline` / `.vline` | hairline connectors |
| `.dot.low` / `.medium` / `.high` | status dots, only for status / level |
| `.row` / `.col` / `.grow` | flex helpers |
| `<i class="link" …>`, `data-tree-from` | connectors drawn by `diagram.js` (elbow, tree, curve, straight, arrows): engine-html.md → Lines |
| `data-cat` + `.cat-fill` / `.cat-line` / `.cat-text` / `.cat-dot` | decorative category colors, active only with `--colors palette` (themes.md → Decorative colors) |
| inline `<svg>` | anything geometric (circles, lenses, arcs, arrows, curved connectors). Stroke and fill **only** via `var(--d-*)` |

Colors only through `--d-bg`, `--d-text`, `--d-subtle`, `--d-line`, `--d-outline`, `--d-accent`,
`--d-on-accent`, `--d-accent-line`. Never a hex in a diagram file: that's what makes every theme work
from one source.

## 3. Composition rules

- **One focal point.** At most one accent **fill** per diagram (the answer, the overlap, the best
  quadrant, the hub). Accent **outlines** may mark a small set ("top 5", "the recommended option").
- **No redundant text.** If two cells would say the same thing, merge them into one element that spans
  both.
- **Labels from the content**, verbatim or faithfully shortened, about 5 words max. Examples only where
  the placeholder asks for them, consistent with the text.
- **No decoration that carries no meaning:** no icons, logos, illustrations, gradients, shadows, 3D,
  textures. Abstract bars stand in for "a document" or "rows of data", never fake readable text.
- **Reading order** left → right, top → bottom. Arrows only where direction matters.
- **Alignment:** everything on a grid; equal gaps; headings in a row on the same baseline.
- **Max 3 type levels** (heading → label → supporting text).

## 4. Works everywhere (one image for desktop and phone)

Article images are `max-width: 100%`, about 358 px wide on a phone. Design for both at once:
- Canvas 1200 CSS px wide; text never below 34 px (≈ 10 px on a phone), labels 44, headings 56.
- Ratio 4:3 by default; anything between 16:9 and 3:4 is fine when the content needs it. Prefer
  stacking to stretching: 5+ steps go vertical, lanes put their name on its own row.
- About 12 labels and 4 columns at most. More than that → split into two diagrams or simplify, and say so.
- Many items (a sitemap, a long tree): show the children as a **text list with a hairline on the left**
  instead of pills (a pill costs ~1.5× the height and wraps sooner), and put groups in 2 columns.
  Paths, URLs and codes get `white-space: nowrap`, so they never break at a hyphen.
- The same word twice (a group called "Tools" holding a page called "Tools") is redundant text: name
  the group by what sets it apart ("Outside the menu").
- Check the 358 px preview. If it isn't readable, change the layout; a separate `-mobile` version only
  when the user asks (showing it needs a `<picture>` change in brackets-web).

## 5. Approved examples (style references)

Each one is in `assets/examples/` with EN + SK labels (the first five from the UX-audit article, the sitemap from brackets-web itself) and was approved in the
reference run. The Higgsfield line is the `CONTENT` description that produced the approved image.

| File | Shows | Higgsfield `CONTENT` description |
|---|---|---|
| `comparison.html` | two-panel bad → good; one subgrid aligns column labels, top rows and the rest | Left heading + tall rounded document of identical placeholder bars; right heading + column-label row + five accent-outlined pill rows numbered 1–5 with abstract bars + thinner secondary bars labelled "Ranked rest"; small accent arrow left → right. |
| `timeline.html` | numbered steps (vertical) with a branch into quiet pills | Thin horizontal line, N accent-outlined numbered circles, label under each; from node K a thin branch drops to 2–3 small outlined pills. Crop in post. |
| `venn.html` | SVG circles + lens, HTML text placed over it | Two outlined circles with labels (+ secondary sublabel); overlap filled with the accent and dark text; a small secondary label in each non-overlap part; one outlined pill centered below for the third case. |
| `matrix.html` | 2×2 with labelled axes, best quadrant filled | X axis label with low/high ends, Y axis label with low/high ends; four rounded quadrants with hairline outlines; the best quadrant filled with the accent; each quadrant = title + secondary example. |
| `swimlane.html` | before / after lanes around a central accent bar; one lane spans the bar | Headers "Before …" / "After …"; one tall vertical accent pill in the middle with a rotated label; one lane per item: name + small outlined sample pill, outlined pills left/right of the center, thin connectors; the more common option outlined in the accent; a lane where before = after is ONE long pill spanning across. |
| `sitemap.html` | sitemap of meetbrackets.com: root → bus → 2 columns of groups, pages with mono paths, children as a hairline list; real counts | (html engine only; the Higgsfield test of the same layout is in engine-higgsfield.md §2) |
| `uml-types.html` | taxonomy (UML 2.5, 14 types): root → rounded bus into two family cards, a nested group, accent outlines for "start here", legend in the free corner; families carry `data-cat` (renders mono or `--colors palette`) | (html engine only) |
| `spider.html` | spider / mind map: hub (accent fill) → four branches in the quadrants → three leaves each pointing outwards; straight `radial` lines trimmed at the outlines; leaves carry `data-cat` per branch (mono by default, `--colors palette` colors them). Form taken from a user's Miro reference. | (html engine only) |

## 6. Growing this file

When the user approves a diagram of a new kind, add it: the HTML to `assets/examples/<name>.html`
(labels as `data-l` pairs), and a row to the table in section 5 (plus the `CONTENT` text if it was made
with Higgsfield). Add a row to section 1 if it covers a content shape that isn't listed.
