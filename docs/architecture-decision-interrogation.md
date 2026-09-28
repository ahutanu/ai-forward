---
id: architecture-decision-interrogation
title: "Decision Interrogation Architecture"
type: architecture
status: accepted
owner: "@timmalloo"
phase: "decision-interrogation"
tags: [skills, conversation, portability]
links:
  - { to: spec-decision-interrogation-protocol, rel: implements }
  - { to: adr-0013-conversation-native-interrogation, rel: depends-on }
review-by: 2027-03-27
summary: >-
  Implements decision interrogation as shared skill guidance executed inside the current
  conversation, with no separate runtime or persistence subsystem.
---

# Decision Interrogation Architecture

## Shape

The architecture has two parts:

1. `pack/knowledge/decision-interrogation.md` defines the shared dialogue contract.
2. The four authoring skills invoke that contract at their required insertion points.

The active harness provides the interaction primitive. A structured question tool is preferred;
plain chat is the fallback. The current skill owns its in-memory question list and writes only the
normal artifact it already owns.

## Boundaries

- The protocol does not call a model separately from the active skill.
- The protocol adds no data store, Git ref, identity system, security boundary, or telemetry.
- Existing audit, repository, and conversation behavior remains unchanged.
- Portability comes from semantic guidance, not a host-specific API contract.

## Delivery slices

1. Shared contract plus `/specify`.
2. `/ui-design`, `/define-architecture`, and `/design-slice`.
3. Regression tests and generated pack surfaces.

## Residual risk

Hosts differ in how they present structured questions. The semantic fallback is one plain chat
question at a time.
