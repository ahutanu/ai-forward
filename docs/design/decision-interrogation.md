---
id: design-decision-interrogation
title: "Decision Interrogation Skill Design"
type: design
status: accepted
owner: "@timmalloo"
phase: "decision-interrogation"
tags: [skills, dialogue]
links:
  - { to: architecture-decision-interrogation, rel: refines }
  - { to: spec-decision-interrogation-protocol, rel: implements }
review-by: 2027-03-27
summary: >-
  Defines the reusable question table, serial question loop, insertion points, and fast path used
  by the four authoring skills.
---

# Decision Interrogation Skill Design

## Shared contract

Each skill builds a short list of unresolved consequential questions. A question is consequential
only when its answer changes the artifact, acceptance criteria, architecture, or design direction.
The skill resolves facts itself and does not ask the human to do research it can perform.

Before asking, render:

| Question | Needed for | Recommendation |
|---|---|---|
| concise decision question | artifact choice it controls | preferred answer and one-line reason |

Then ask one question at a time. After each answer:

1. record the decision in the working artifact;
2. remove questions made irrelevant;
3. add a newly exposed question only when it is consequential;
4. stop when the list is empty or the human defers the remaining decision.

## Insertion points

| Skill | During authoring | Before handoff |
|---|---|---|
| `/specify` | Before settling scope, user need, UX flow, or UI archetype when evidence does not decide | Yes |
| `/ui-design` | Before settling direction, archetype, density, interaction, or visual trade-offs | Yes |
| `/define-architecture` | Facts are researched; human product/constraint forks are recorded for closure | Yes |
| `/design-slice` | Facts are researched; unresolved component trade-offs are recorded for closure | Yes |

## Question shape

Each question contains:

- the question;
- what it is needed for;
- the recommendation and reason;
- suggested choices where useful;
- a free-form answer path;
- defer only when the dependent artifact section can remain explicitly unresolved.

## Proof

Static regression tests assert that the shared contract and all four insertion points remain wired.
The existing skill evals provide behavioral regression coverage.
