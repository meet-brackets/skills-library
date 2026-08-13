# Connectors

Skills in this library work standalone, but some steps light up when you connect external tools (via MCP servers or CLIs). Skill files reference these with `~~placeholder` names so they stay tool-agnostic — substitute whatever you actually have connected.

| Placeholder | What it means | Examples |
|---|---|---|
| `~~source control` | Where your code and PRs live | GitHub (`gh` CLI), GitLab, Bitbucket |
| `~~project tracker` | Where tickets and requirements live | Jira, Linear, GitHub Issues |
| `~~knowledge base` | Where team docs and standards live | Confluence, Notion, a `docs/` folder |

## How skills use these

When a skill says "If **~~source control** is connected", it means: if a matching tool is available in the current session (an MCP server or an authenticated CLI), use it for that step. If nothing matches, skip the step — the skill's standalone path always works.

## Checking what's connected

- MCP servers: run `/mcp` in Claude Code, or check `.mcp.json` / `claude mcp list`.
- CLIs: check for authenticated tools like `gh auth status`.
