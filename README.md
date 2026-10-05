# Skills Library

A library of reusable Claude Code skills. Each skill lives in `skills/<name>/SKILL.md`.

## Skills

| Skill | Description |
|---|---|
| [article-meta-generator](skills/article-meta-generator/SKILL.md) | Generate publishing metadata for a finished BRACKETS /thinking article. |
| [code-review](skills/code-review/SKILL.md) | Review code changes for security, performance, and correctness. |
| [article-illustration](skills/article-illustration/SKILL.md) | Generate a 3-color risograph header illustration for an article in a BRACKETS palette color rotated against the latest /thinking articles, with an optional seamless looping MP4 (< 1 MB, optimized automatically, no setup). |
| [content-diagrams](skills/content-diagrams/SKILL.md) | Turn `[VIZUÁL]` placeholders or a request into flat diagrams in the meetbrackets.com design system (any type that fits the content), per language and per surface theme, rendered from HTML/SVG with the real Poppins by default (no credits), Higgsfield only on request, then placed into the content with alt text. |
| [ai-disclosure](skills/ai-disclosure/SKILL.md) | Burn the official EU AI-disclosure icon into an image after generation (subtle basic `AI` icon by default, `AI GENERATED` / `AI MODIFIED` on request), with AI Act classification. |
| [security-review](skills/security-review/SKILL.md) | Security-only blacklist review of a Laravel + Inertia diff: authorization, injection, data exposure, secrets, dependencies. |

## Using a skill

Copy the skill folder into a project's `.claude/skills/` directory (or your global `~/.claude/skills/`), then invoke it with `/<name>` — e.g. `/code-review <PR URL or file path>`.

Some skills reference `~~connector` placeholders — see [CONNECTORS.md](CONNECTORS.md).
