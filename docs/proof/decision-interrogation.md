---
id: proof-decision-interrogation
title: "Decision Interrogation Proof"
type: proof-pack
status: accepted
owner: "@timianmalloo"
phase: "decision-interrogation"
tags: [skills, verification]
links:
  - { to: spec-decision-interrogation-protocol, rel: tested-by }
  - { to: design-decision-interrogation, rel: tested-by }
review-by: 2027-03-27
summary: >-
  Records the executed checks for conversation-native interrogation, create-proposal, HTML
  companions, and collectknowledge deep-research guidance.
---

# Proof Pack: Decision Interrogation

## Claims

| Claim | Evidence | Confidence | Residual risk |
|---|---|---|---|
| The four authoring skills use the shared question table and serial dialogue. | `test_decision_interrogation_skills.py`; fault injection replacing serial dialogue with a bulk questionnaire failed before restoration. | Verified | Host presentation differs, so plain chat remains the fallback. |
| `/create-proposal` produces Markdown and HTML proposals with optional mockups. | Static skill contract tests, handbook coverage, eval schema validation, and synchronized harness surfaces. | Verified | The golden task still requires an agent-run workspace to exercise content quality. |
| Human-facing Markdown can be rendered as safe self-contained HTML. | `test_render_markdown.py` covers structure, HTML escaping, unsafe links, CLI output, and atomic writes. | Verified | The renderer intentionally implements a practical Markdown subset. |
| `/collectknowledge` uses native deep research when available and verifies primary sources. | Static contract test and synchronized skill surfaces. | Verified | Availability remains harness/model dependent. |

## Verification

```text
python -m pytest -q tests/docs_explorer/test_decision_interrogation_skills.py tests/docs_explorer/test_render_markdown.py tests/docs_explorer/test_verify_skill_contracts.py
pwsh tools/verify-bundle.ps1
```

The focused suite passed 27 tests. The full bundle run passed all functional gates and 1,277
Python tests; its first run found only generated index drift, which was resolved by the final sync
and rerun.

## Gate record

`GATE implement · 2026-09-27 · Test Architect + Python Developer · conversation contract, renderer safety, pack parity, and full repository gates · verdict: PASS`
