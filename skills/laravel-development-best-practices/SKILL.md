---
name: laravel-development-best-practices
description: Team-approved Laravel best practices distilled from real code-review feedback on Brackets projects (e.g. Calma). Use when writing, planning, or reviewing Laravel/PHP code — especially business rules, listeners, notifications, models and admin-configurable behaviour — to avoid patterns that reviewers have already rejected.
---

# Laravel Development Best Practices

A living collection of rules learned from code-review feedback. Each rule records **what** to do, **why**, and the **source** (PR / ticket) where the feedback came from.

## How to use

- **When implementing:** read the rules below before designing a change, and follow them unless the task explicitly says otherwise.
- **When reviewing:** check the diff against every rule; cite the rule number in findings.
- **When adding feedback:** append a new rule using the template at the bottom. Keep rules general (a principle), with the concrete case as the example.

---

## Rules

### 1. Make business rules explicit data, not hardcoded name matching

**Rule:** Don't drive behaviour by pattern-matching on user-editable strings (names, titles, labels) in code. When some records need to behave differently, add an explicit, admin-configurable attribute (boolean / enum column) on the model or template that owns the behaviour, and branch on that.

**Why:**
- Names are content, not configuration — an admin renaming `Bonus 79` → `Bonus credit 79` silently changes system behaviour.
- The rule is invisible to the people managing the data; they can't see or control it from the admin.
- Every new variant requires a code change and deploy instead of ticking a checkbox.
- Magic regexes/constants in listeners scatter domain logic away from the model that owns it.

**Do:**
```php
// Migration: add a flag to the template that owns the behaviour
$table->boolean('notify_client')->default(true);

// Copy the flag onto the transaction when it's created from the template,
// then in the listener:
if (! $event->transaction->notify_client) {
    return;
}
```
Expose the flag as a checkbox in the admin form for the template.

**Don't:**
```php
private const BONUS_TRANSACTION_NAME_PATTERN = '/\ABonus \d+\z/u';

if ($event->transaction->value > 0 && preg_match(
    self::BONUS_TRANSACTION_NAME_PATTERN,
    trim((string) $event->transaction->name)
) === 1) {
    return;
}
```

**Source:** [meet-brackets/calma#319](https://github.com/meet-brackets/calma/pull/319) — "Disable Bonus credit notifications" (ticket #679 / CAL-601). Closed by reviewer: *"Closed due to bad architecture. We will do it by adding a boolean/checkbox to the fee/transaction templates which will serve this purpose."* Note that the automated agent review approved the PR — it checked correctness (debits vs. credits) but missed the architectural problem. Architecture review must ask *"where should this decision live?"*, not just *"does it work?"*.

---

## Template for new rules

```markdown
### N. <Short imperative title>

**Rule:** <The principle in 1–2 sentences.>

**Why:** <Reasons the reviewer gave, plus consequences.>

**Do:** <Preferred code/approach.>

**Don't:** <Rejected code/approach, ideally from the PR.>

**Source:** <PR link> — <title> (<ticket>). <Reviewer's quote.>
```
