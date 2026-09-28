---
id: spec-decision-interrogation-protocol
title: "Decision Interrogation Protocol"
type: spec
status: accepted
owner: "@timmalloo"
phase: "decision-interrogation"
tags: [skills, questions, workflow]
links: []
review-by: 2027-03-27
summary: >-
  Defines a lightweight, question-first dialogue for resolving consequential unknowns in
  authoring skills without introducing a new persistence, identity, security, or privacy layer.
---

# Decision Interrogation Protocol

## Goal

Help the human and AI make important decisions early, without slowing down work that is already
clear. This is a conversational workflow. It has the same trust, privacy, and persistence
characteristics as the surrounding prompt conversation.

## Required behavior

1. `/specify` and `/ui-design` identify consequential unknowns before they settle the affected
   requirement or visual direction.
2. `/specify`, `/ui-design`, `/define-architecture`, and `/design-slice` run a closure check before
   handoff.
3. If no consequential question remains, the skill continues without extra ceremony.
4. If questions remain, the skill first shows one compact table:

   | Question | Needed for | Recommendation |
   |---|---|---|

5. The skill then asks the questions one at a time using the harness's structured question tool
   when available, or one ordinary chat question at a time otherwise.
6. Each question offers a recommendation and a short reason. The human may accept it, choose
   another answer, defer it, or provide a free-form answer.
7. After each answer, the skill updates its understanding and removes questions that are no longer
   relevant.
8. A deferred question blocks only the artifact section that genuinely depends on it. The skill
   marks that section unresolved rather than inventing an answer.
9. The final artifact records the decisions that shaped it and lists any remaining open questions.

## Non-goals

- No custom decision ledger, Git ref, signing system, identity proof, provider router, or background
  workflow.
- No duplicate security or privacy model beyond the current conversation and repository.
- No interrogation for facts the agent can cheaply establish itself.
- No bulk questionnaire when later questions depend on earlier answers.

## Acceptance criteria

- A clear task completes without an interrogation round.
- A consequential unknown produces the summary table before the first question.
- Questions are asked serially, and later questions may change after an answer.
- Every question says what decision it enables and includes a recommendation.
- The four target skills run the closure check before handoff.
- `/specify` and `/ui-design` also use the protocol during authoring when an early answer prevents
  wasted work.
- The behavior works in Copilot, Claude Code, Codex, Grok, and Agy by using each host's native
  question mechanism or plain chat fallback.

# Part B - UX

The interaction is a short guided sequence: orientation table, one active question, answer,
updated next question, closure summary. The user can accept the recommendation quickly or provide
another answer. Progress is shown as `Question N of M` only when the remaining count is known.

# Part C - UI

The primary surface is the host conversation. No custom application UI is required. Tables,
structured choices, and concise status text use native host rendering.
