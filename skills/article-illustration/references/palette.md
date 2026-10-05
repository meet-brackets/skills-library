# BRACKETS illustration palette

The **only** colors an illustration background may use. Source of truth:
`brackets-web/src/styles/tokens/colors.css` (the web design system). If that file changes, update
this table and `PALETTE` in `scripts/recent_colors.py` together.

| Name | Token | Hex | Light? |
|---|---|---|---|
| Carribean Green | `--color-carribean-green` | `#34D399` | yes |
| Supernova | `--color-supernova` | `#F5A816` | yes |
| Biloba Flower | `--color-biloba-flower` | `#9333EA` | |
| Princess Perfume | `--color-princess-perfume` | `#DB2777` | |
| Deep Sky | `--color-deep-sky` | `#22D3EE` | yes |
| Crusta | `--color-crusta` | `#F97316` | |
| Cornflower Blue | `--color-cornflower-blue` | `#2563EB` | |
| Blue Violet | `--color-blue-violet` | `#4F46E5` | |
| Radical Red | `--color-radical-red` | `#F43F5E` | |
| Keppel | `--color-keppel` | `#14B8A6` | |

- The name column is the design-system spelling ("Carribean" included). Use it as `{COLOR_NAME}`.
- **Light? = yes** triggers the light-primary rule in the prompt ("keep black outlines heavy so white
  shapes stay readable against the light background").
- Supernova's lock icon in the design system only marks the web primary color. For illustrations it
  rotates like every other color.
