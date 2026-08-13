# Skills Library

A library of reusable Claude Code skills. Each skill lives in `skills/<name>/SKILL.md`.

## Skills

| Skill | Description |
|---|---|
| [code-review](skills/code-review/SKILL.md) | Review code changes for security, performance, and correctness. |

## Using a skill

Copy the skill folder into a project's `.claude/skills/` directory (or your global `~/.claude/skills/`), then invoke it with `/<name>` — e.g. `/code-review <PR URL or file path>`.

Some skills reference `~~connector` placeholders — see [CONNECTORS.md](CONNECTORS.md).
