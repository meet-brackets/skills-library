---
name: article-meta-generator
description: Generate the full set of publishing meta fields for a finished BRACKETS /thinking article — title, slug, author, topic, excerpt, meta title, meta description, related pages, and OG image. Use this whenever Pavol (or anyone on the BRACKETS content side) has an article draft agreed and ready to publish and needs the CMS fields filled in. Trigger on phrases like "generate the meta", "fill in the article fields", "what should the title/slug/excerpt/meta be", "prep this for publishing", "publishing fields", "SEO fields for this article", or any time an agreed article draft needs its Content Studio / CMS metadata produced. Also trigger when the user pastes a finished article and asks what to put in the publishing form. Do NOT use this for drafting or editing the article body itself (that is normal content work) or for LinkedIn post fields (that is the draft-linkedin-post MCP tool).
---

# Article Meta Generator

Produce every publishing field for a finished BRACKETS /thinking article, in one pass, each field written for the specific job it does. This exists because the same article feeds several surfaces (the page, Google's results, an LLM's citation, a social preview, the on-site article card) and those surfaces want different things from the same words. Filling every field with the same sentence wastes most of them.

## When to run
The article body must already be **agreed and essentially final**. This skill does not draft or restructure the article. If the draft is still moving, finish that first. The only edit this skill makes to the body is flagging internal inconsistencies it notices while reading (see step 1).

## The governing principle: every field has one master

Before writing anything, hold this in mind. Each field primarily serves either **SEO/GEO** (machines: search ranking, LLM citation, topical authority, internal link equity) or **engagement** (humans: earning the click, warmth once they're already reading). A few serve both and carry a built-in tension that must be managed deliberately rather than collapsed.

| Field | Primary master | What that means in practice |
|---|---|---|
| Slug | SEO only | Keyword-bearing, short, lowercase-hyphenated. Immutable once shared. |
| Title (H1) | Engagement first, SEO second | The human reads this on the page and in social previews. Can be witty at the keyword's expense — the meta title carries the SEO load. |
| Meta title | SEO + SERP click-through | Different surface from the H1. Keyword unambiguous, brand suffix here. May and often should differ from the H1. |
| Meta description | Click-through + GEO citation | Not a ranking factor. Answer-first so an LLM can lift it. The sales pitch in the results list. |
| Excerpt | On-site engagement | The card blurb / internal-link teaser. Reader is already warm, so more voice than the meta description. Must not be identical to it. |
| Topic / category | Site architecture (SEO via topical clustering) | Serves internal linking, not the reader directly. |
| Author | E-E-A-T + GEO | Attributed expertise is a trust/ranking signal. Always a real person. |
| Related pages | SEO (link equity) + secondary engagement | Pillar page + cluster siblings + relevant case narratives. |
| OG image | Engagement only | Pure social click-through, zero SEO weight. Consistency with the post's card is the win. |

**The two tensions to manage every time (do not collapse them):**
1. **Title vs meta title** — let the H1 be human, let the meta title be keyword-safe. They are allowed to differ.
2. **Excerpt vs meta description** — excerpt is warm (reader is on the site); meta description is answer-first (machine may cite it, stranger may click). Write them differently on purpose.

## Step 1 — Read the article for consistency first
Before generating fields, read the full body once and flag any internal contradictions to the user (conflicting numbers, timelines, or claims). The meta fields inherit the article's logic, so a glitch in the body propagates. Report it, let the user fix the body, then proceed. Do not silently "correct" the article.

Also note, while reading: the single strongest concrete anecdote, the core thesis in one sentence, the primary keyword a prospect would actually search, and any real numbers — these feed the fields below.

## Step 2 — Generate the fields

Produce all of these. Show the reasoning briefly only where a choice is non-obvious; otherwise just give the value.

**Title (H1)**
The on-page headline. Human-first. If the agreed article already has a title the author likes, keep it unless it actively hurts (misleading, or zero keyword when a natural one was available). Do not "SEO-ify" a good human title — that is the meta title's job.

**Slug**
Lowercase, hyphenated, short (aim ≤5 words), must contain the primary keyword. **Critical:** if a LinkedIn post or anything else has already been scheduled/published pointing at this slug (check the conversation for a first-comment URL), the slug is LOCKED — reuse it exactly or the link breaks. Never silently change a slug that's already committed elsewhere.

**Author**
The real person, matching the persona who wrote it (Pavol Perdík → product/strategy/partnerships; Samuel Trsťanský → architecture/engineering; Karol → delivery/ops). Never "BRACKETS Team" — E-E-A-T and GEO both reward a named human, and it fits the positioning.

**Topic** (enum — pick exactly one)
`building-right` · `engineering` · `partnerships` · `strategy` · `trust-and-ai`
Map by the article's core question: build-vs-buy / economics / SaaS / business model → `strategy`; architecture, quality, how-it's-built → `engineering`; choosing/working-with a partner, agency evaluation → `partnerships`; credibility, authenticity, human-proof, AI noise → `trust-and-ai`; the craft/discipline of building well (clarity before code, what to build) → `building-right`.

**Excerpt** (~25–35 words)
The on-site card blurb. Warm, voice-y, makes a reader already on /thinking click through. Can pose the tension or tease the payoff. Must NOT be a copy of the meta description.

**Page title / meta title** (≤60 characters incl. suffix)
Keyword-clear, then ` | BRACKETS`. This is the SERP and social-title surface. It may restate the H1 more literally to capture the query. Count the characters — 60 is a hard ceiling.

**Meta description** (≤155 characters)
Answer-first (per BRACKETS GEO strategy): state the article's conclusion plainly so an LLM can cite it and a stranger can decide to click. No clickbait, no "read on to find out". Count the characters — 155 is a hard ceiling.

**Related pages**
Pick from: the relevant pillar page (Own Your Software / Build & Deliver / Product & Discovery / AI & Modern Tech / Fractional Leadership), cluster-sibling articles (from the ideaboard cluster this idea belongs to), and any live case narrative on the same topic. At launch, if siblings don't exist yet, point at least to the pillar so there's one internal link. Name the ideaboard cluster if the article maps to one.

**OG image**
Default: **reuse the LinkedIn post's OG card** if this article ships with a post (same two-line headline + orange pill highlight word) — visual consistency across post and article is the win, and it's already rendered. Follow `og-image` rules: two lines, ~≤36 chars, comma after line one, highlight one word in the pill. If there's no companion post, propose a fresh two-line headline in the same style. BRACKETS is typography-led / no stock photos — a text card is the right call for /thinking pieces; only suggest a photo when the article is genuinely about a real event/team moment.

## Step 3 — Output format
Give the fields as a clean labelled list the user can paste into the Content Studio / CMS form, in the form's field order:
title · slug · author · topic · excerpt · related pages · page title (meta title) · meta description · OG image.
Put the character count in parentheses after meta title and meta description so the user can see the limits are met. Keep commentary minimal — this is a fill-in-the-form deliverable, not an essay.

## Voice reminders (inherited from BRACKETS positioning)
Calm, senior, direct, non-hype, no buzzwords, no overclaiming. No em dashes in any field (house rule). The meta fields should sound like the article, not like marketing wrote a wrapper around it.
