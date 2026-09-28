---
id: adr-0013-conversation-native-interrogation
title: "Use conversation-native decision interrogation"
type: adr
status: accepted
owner: "@timmalloo"
phase: "decision-interrogation"
tags: [skills, conversation]
links:
  - { to: architecture-decision-interrogation, rel: refines }
review-by: 2027-03-27
summary: >-
  Chooses shared prompt guidance and native host questions instead of a new decision-runtime
  subsystem.
---

# ADR-0013: Use conversation-native decision interrogation

## Decision

Implement interrogation inside the active authoring skill. Use the host's structured question
facility when available and plain chat otherwise. Persist decisions only in the artifact the skill
already produces.

## Why

The original need is conversational: surface the important questions, explain why they matter,
recommend an answer, and resolve them one by one. A separate ledger, authority model, or Git
protocol would add complexity without improving that experience.

## Rejected

- **Custom decision runtime and ledger:** rejected as unnecessary infrastructure.
- **Ask every question up front:** rejected because later questions may depend on earlier answers.
- **Never ask and rely on assumptions:** rejected because consequential product decisions belong to
  the human.
