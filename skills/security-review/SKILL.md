---
name: security-review
description: Security-only review of a Laravel + Inertia/React diff against a fixed blacklist — authorization and tenant scoping, injection, data exposure, secrets, webhooks, sessions, dependencies, supply chain. Trigger on any pull request review, "is this safe to ship", "security check this diff", or when a change touches routes, policies, guards, uploads, raw SQL, HTML rendering, env vars or lockfiles.
argument-hint: "<PR URL, diff, or base branch>"
---

# /security-review

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../../CONNECTORS.md).

A doorman's pass over one diff. It is not a general code review — run `code-review` for
correctness, performance and style — and it does not fix anything. It reports findings, each with
one severity, and says whether any of them blocks the merge.

## Usage

```
/security-review <PR URL, diff, or base branch>
```

Review: @$1

Without an argument, review the current branch against `develop` if it exists, else `main`.

## How to review

- **Exhaustively.** Read every changed file end to end, follow call sites, trace data flow from
  request to persistence and back to the response. Verify against the code, not the diff's
  implication, and not the PR description.
- **Stated intent vs. actual diff.** The PR title, body and linked ticket are a claim to verify.
  Report scope creep only when it carries security weight — a drive-by permission change, a new
  route, a loosened validation rule.
- **Run the audits when lockfiles changed** (see *Dependencies*). A failed audit command is a
  finding, not a pass.
- "Not touched by this diff" is a valid outcome per item. "Did not check" is not.

## The blacklist

Anything on this list does not get in. Check every item against the diff, in the worktree,
following call sites — never from the diff alone. "Not touched by this diff" is a valid outcome per
item; "did not check" is not.

*Authorization and identity*
- Every new or changed route, controller action, Inertia page prop, MCP tool and API endpoint has an
  explicit authorization check (policy, `can`, gate, or route middleware). A middleware group alone is
  not object-level authorization; a hidden button in the frontend is not authorization at all.
- Routes: no `Route::any`, no `->withoutMiddleware(...)`, no new route outside the `auth` group
  without a stated reason; `authorizeResource`/policy method names match the actions they guard;
  a policy `before()` or a method returning `true` unconditionally is a finding.
- IDOR: route model binding and query parameters scoped to the authenticated user/client/project
  (`scopeBindings()` on nested resources); no lookup by bare id on a record the caller does not own.
- Tenant scope bypass: `withoutGlobalScope(s)`, `Model::query()` on a tenant-scoped model from a
  shared context, or a relation walked from a model the caller does not own.
- Background context: queued jobs, listeners, notifications, scheduled commands and MCP tool
  handlers run without the request's guard. Anything they do on behalf of a user re-checks
  authorization from the ids they were given, and job payloads do not serialize secrets.
- State machines: status/role/plan transitions validated with `Rule::in`/enum against the ALLOWED
  next states for this caller, not just against the enum's full list.
- Guard confusion: staff (`web`), client (`client`) and API (`api`/Passport) guards resolved
  correctly; a route reachable on one guard does not leak another guard's data. Impersonation paths
  keep the impersonator's limits.
- Role/permission changes (Spatie): new permissions registered to the intended roles only; no
  widening of an existing role in passing.
- Passport/OAuth, session, remember-me, password reset, 2FA, invitation and impersonation code paths
  are always at least High if changed, and named on the "Sensitive paths touched" line so the
  release gate knows a human must merge.

*Input and data*
- Validation on every write: a spatie `Data` object or equivalent; no `$request->all()` into
  `create()`/`update()`; `$fillable`/`$guarded` intact; no `Model::unguard()`.
- SQL: no interpolation into `whereRaw`, `selectRaw`, `orderByRaw`, `DB::statement`; bindings used.
  Postgres-specific operators (`ilike`, JSON ops) still parameterized. Column and direction names
  from the request (`orderBy($request->sort)`, `select($request->fields)`, `where($request->only())`)
  are allow-listed — bindings do not protect identifiers.
- Command and code execution: no request data in `exec`/`shell_exec`/`Process::run`, `unserialize`,
  `eval`, dynamic `view()`/`include`, or `Storage::get($path)` (path traversal).
- Rich text and HTML: everything rendered with `dangerouslySetInnerHTML`, `{!! !!}` or `v-html`
  passes the project sanitizer; sanitizer allow-list not widened; base64 image handling bounded;
  user-controlled `href`/`src` reject `javascript:` and `data:` schemes; markdown renderers run in
  safe mode.
- File uploads: type/size/extension allow-list, media-library collections with correct disk
  visibility, no user-controlled paths, no executable content served from a public disk.
- Mass data exposure: new Inertia props (including shared props in `HandleInertiaRequests`), API
  resources, Blade view data, MCP tool outputs and notifications do not serialize `$hidden`
  attributes, tokens, hashes, internal ids of other tenants, or whole models where a subset suffices.
- Storage of sensitive data: new columns holding tokens, API keys or personal data use the
  `encrypted` cast or a hash; tokens are unique-indexed and compared with `hash_equals`, not `==`.
- Randomness and hashing: `Str::random`/`random_bytes` for tokens, never `rand`/`uniqid`/`md5`
  of predictable input; passwords only through `Hash`.
- Agent-facing input: text a client wrote (ticket bodies, comments, attachments) reaches LLM agents
  through MCP tools. New tool outputs return data, not instructions; nothing lets ticket content
  alter what a tool does with other tenants' data.

*Secrets, config, outbound*
- No credentials, tokens, signing keys or private URLs in code, fixtures, seeders, tests or docs.
- New env vars, secrets, third-party services, webhooks, queues or crons: name each one (the
  release gate blocks on them; your job is to say whether the integration is safe as written).
- Webhook and callback endpoints verify signatures (Mailgun, Slack, GitHub, Jira) with a
  constant-time compare and reject on missing signature; replay window considered.
- Outbound HTTP: no user-controlled destination (SSRF); redirects only to allow-listed targets.
- Logging: no PII, secrets or full request bodies in `Log::` calls; exception messages not exposed
  to the client; no `APP_DEBUG`/`config('app.debug')` toggles, Telescope/Debugbar/Horizon routes
  or verbose error pages reachable in production.
- Mail and notifications: user-controlled recipient or body content is bounded and rate-limited
  (no open mail relay through a "share"/"invite" endpoint); links use signed URLs with an expiry
  and the route carries `signed` middleware.

*Sessions, CSRF, headers*
- State-changing requests are not on GET and are inside CSRF protection; explicit CSRF exclusions
  justified and signature-verified instead.
- Rate limiting present on auth, invitation, password, token and public-form endpoints.
- Cookie/session flags, CORS and security headers unchanged or tightened.
- Login paths: `Auth::login`/`loginUsingId` only after the proof was verified (invitation token,
  magic link, OAuth state), never from a request parameter alone; sensitive changes (email,
  password, 2FA) require the current password or a fresh session.
- Concurrency: quota, balance, uniqueness and "first one wins" checks hold under a lock or
  transaction (`lockForUpdate`, unique constraint), not a read-then-write.

*Dependencies*
- When `composer.lock` changed: run `composer audit --locked --format=summary` (falls back to
  `composer audit`) in the worktree. When `package-lock.json` changed: `npm audit --omit=dev
  --audit-level=high`. Any High/Critical advisory in a production dependency is a High finding;
  a failed audit command is reported as such, not as a pass.
- Major-version bumps of auth, crypto, HTTP, or serialization libraries are at least Medium.
- Supply chain: new `composer.json`/`package.json` scripts, new or unpinned third-party GitHub
  Actions, `pull_request_target` workflows, or secrets newly passed into a workflow are at least
  Medium; a new dependency from an unknown publisher is named in the review.

*Tests and CI as evidence*
- A diff that deletes, skips or loosens an authorization, validation or signature test is a
  finding at the severity of what the test protected.
- Auth/authz changes without a test covering the denied path are Medium ("authorization untested"),
  even when the code reads correctly.

## Severity

One severity per finding, placed by impact × likelihood. Answer "what happens if this ships" and
"how likely is it" before choosing. Do not hedge into Medium.

| Severity | Meaning | Blocking |
| --- | --- | --- |
| Critical | Exploitable now: missing authorization on a data-bearing endpoint, injection, secret in repo, auth bypass | yes |
| High | Real weakness with bounded blast radius: IDOR on a non-critical record, unsigned webhook, sensitive field serialized, vulnerable production dependency | yes |
| Medium | Hardening gap that is not exploitable as written: weak-but-unexploitable validation, missing rate limit on a low-value endpoint, over-broad but authorized prop | no, listed |
| Low | Hygiene: logging verbosity, minor header, naming of a permission | no, listed |


## Output

Findings only — no praise, no recap, no narration.

```markdown
## Security review: <PR title or branch> @ <head sha>

**Blocking: yes|no**

#1 · `app/Http/Controllers/SlotController.php:42` · High · store() has no policy check → authorize('create', Slot::class)
#2 · …

Medium/Low (n shown, m cut):
- `app/Models/Ticket.php:18 — token column stored in plaintext → encrypted cast`

Sensitive paths touched: authentication, authorization | none
```

- Every Critical and High numbered from `#1` by severity, one line each: file:line · severity ·
  issue · fix.
- Medium and Low as compact one-liners, capped at ten; say how many were cut.
- The last line names which sensitive areas the diff touches (authentication, authorization,
  payments, sessions, impersonation, invitations, new env vars or third-party services) or `none`.
  A release gate keys off this line to require a human on the merge button.
- If nothing needs fixing: `**Blocking: no**` and one sentence. Stop.

## If Connectors Available

If **~~source control** is connected:
- Pull the PR's head SHA, title, body and diff automatically from the URL, and review the head
  SHA against the base, not the local checkout, unless local HEAD is that SHA.

If **~~project tracker** is connected:
- Read the linked ticket for the stated intent before comparing it with the diff.
