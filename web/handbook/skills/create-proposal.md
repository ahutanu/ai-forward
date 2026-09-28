# Explore an idea before specification

Use this skill to brainstorm a product or feature idea, compare real alternatives, and make the
idea concrete before turning it into accepted requirements.

## When to use it

Use `create-proposal` when the problem, audience, value, or approach is still fluid. Skip it when
the requirement is already clear enough for [specify](#skill-specify).

## What you need

Bring an idea, problem, opportunity, or rough concept. One sentence is enough; related research,
proposals, specs, and mockups are reused when present.

## Try it

Slash-command harnesses:

```text
/create-proposal Explore a lightweight team decision journal. Compare at least two
approaches and recommend one.
```

Codex equivalent:

```text
$create-proposal Explore a lightweight team decision journal.
```

## What happens

The skill frames the opportunity, separates facts from assumptions, compares at least two distinct
approaches, and resolves consequential preferences one question at a time. It may create optional
HTML mockups to test an interaction or visual direction.

## What you get

Illustrative artifact shape:

```text
docs/proposals/team-decision-journal.md
docs/proposals/team-decision-journal.html
docs/mockups/team-decision-journal-entry.html
```

The Markdown and HTML proposal contain the same decisions. The proposal remains exploratory rather
than becoming an accepted specification by implication.

## Review before continuing

Check that the alternatives are genuinely different, assumptions are visible, the recommendation
explains its trade-offs, and unresolved questions are explicit.

## Tips and recovery

If the idea is already settled, move directly to [specify](#skill-specify). If a mockup starts
settling detailed interface rules, use [ui-design](#skill-ui-design) instead.

## Where to go next

Use [specify](#skill-specify) after choosing to turn the proposal into testable requirements.
