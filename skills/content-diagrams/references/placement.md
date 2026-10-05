# Placement: where it renders → which theme

Decide the theme from **where the image will render**, not from the page name. Read the component that
renders the target. State the choice in one line and offer a change.

| Target | Renders on | Theme |
|---|---|---|
| Thinking / Blog article body (`src/content/{thinking,blog}/<slug>.mdoc`, `<slug>/contentSk.mdoc`) | `ArticleDetail.astro` → `ContentSection background="surface-inverse"` | **dark** |
| Page content grid (`src/content/pages/*.mdoc`, `media` block) | `ContentSection`, default `surface-inverse` unless the section sets `background` | read the section: dark / light / dark-subtle / primary |
| Section with `background="surface"` (hero, statement on white) | | **light** |
| Section with `background="surface-inverse-subtle"` | | **dark-subtle** |
| Section with `background="primary"` | | **primary** |
| Section with `backgroundCustom` | the custom CSS value | snap to the nearest theme, say so |
| Case-study content grid | `CaseStudyDetail.astro`: `brand.surface` when set, else `surface-inverse` | **brand** / dark |
| Not on the website (deck, LinkedIn, email, PDF) | | ask once, default dark |

How to verify (brackets-web):
- `src/components/ui/ContentSection.astro`: `background` prop (`'surface' | 'surface-inverse' |
  'surface-inverse-subtle' | 'primary'`, default `surface-inverse`) and `backgroundCustom`.
- `src/components/ui/CaseStudyDetail.astro`: `brand.surface`, `brand.primary`, `lightSurface`.
- Article images get `max-width: 100%` and `border-radius: var(--rounded-md)` (`.page-content img` in
  `ArticleDetail.astro`). A background that is off by a few values shows as a visible rounded box, which
  is why the background has to be the exact token.

## Both versions

The user may want dark **and** light of the same diagram (one for the article, one for a page). The HTML
engine renders both from one source (`--theme light --variant light`). Higgsfield needs a separate
generation per theme.

## File names and locations (brackets-web)

- `<name>-<lang>.png` for the theme of that placement. Extra versions get a suffix:
  `<name>-<lang>-light.png`, `-dark`, `-primary`, `-brand`, `-mobile`.
- **Article bodies:** `src/content/{thinking,blog}/<slug>/content/<file>`, referenced with a bare
  file name: EN `![<EN alt>](<name>-en.png)` in `<slug>.mdoc`, SK `![<SK alt>](<name>-sk.png)` in
  `<slug>/contentSk.mdoc`. `ArticleDetail.astro` resolves them with
  `import.meta.glob('/src/content/{thinking,blog}/*/content/*')` and serves webp. **Only images go in
  that folder**: the glob imports every file, so an HTML source or a preview there breaks the build.
- **Pages / case studies:** `media` content block, image under the entry's own slug
  `@assets/images/content/<slug>/…`. Never reuse another entry's image path (breaks production
  Keystatic, brackets-web `.claude/rules/dont-list.md` → Obrázky).
- Previews (`previews/*-358.png`) and HTML sources stay in the scratchpad, never in the repo. The HTML
  source is embedded in each PNG anyway (`render_diagram.py --extract`).
