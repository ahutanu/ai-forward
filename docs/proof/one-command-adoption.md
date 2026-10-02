---
id: proof-one-command-adoption
title: "Proof Pack — one-command adoption"
type: proof-pack
status: accepted
owner: "@ahutanu"
phase: "pack-adoption"
tags: [adoption, delivery, installation, portability]
links:
  - { to: spec-one-command-adoption, rel: implements }
  - { to: design-one-command-adoption, rel: implements }
review-by: "2027-01-01"
summary: >-
  Executed evidence for conditional outcome delivery and portable source-driven setup,
  including old-code failures, preservation probes, native skill use and finite limits.
---

# Proof Pack: one-command adoption

- **Change:** `feat/one-command-adoption`
- **Spec / design:** `docs/specs/one-command-adoption.md` · `docs/design/one-command-adoption.md`
- **Tier:** T2 (load-bearing workflow boundaries, local state and cross-platform installation)
- **Author / date:** @ahutanu · 2026-10-02

## Claims and evidence

### Claim 1: one named skill selects an applicable route without silently changing the finish line
- **Evidence:** focused delivery, evaluator and adoption controls exercise T0/T1/T2, six
  explicit risk floors, load-bearing architecture, coordination, defect review,
  characterization-before-coordinated-migration, plain-project state, fresh-process
  resume, drift refusal, bound receipts and exact criteria closure.
- **Oracle:** real CLI subprocesses against disposable Git/plain projects and the
  protected golden-case oracle. The controls fail when stages are reordered, evidence
  changes, the contract changes, an author clears an applicable veto, the verifier is
  changed, or product behavior exits before all boundary checks finish.
- **Red observed before green:** yes; routing, proportional review, active-author and
  oracle counterexamples were executed against the pre-fix source.
- **Confidence:** [Verified] for deterministic routing/checkpoint mechanics.
- **Residual risk:** actor/source labels and hashes are cooperative structural controls,
  not proof of semantic correctness or authentic human consent. Model compliance is a
  separate native-host observation.

### Claim 2: setup is one cross-shell command and preserves product work
- **Evidence:** current committed-source fixtures install into both plain and Git
  projects, preserve dirty product bytes and an existing product graph, deploy the exact
  canonical `deliver` skill/helper, create no audit log, and produce byte-identical
  repeat installs. Focused controls cover worktrees, exact refs and hidden commits,
  malformed policy, nonregular paths, rollback, installed-state readback and failures.
- **Oracle:** source-map-derived plans, a disposable staging target, pre-promotion drift
  checks and exact installed-byte readback. Tests explicitly fail if the bootstrap scans
  dependency trees, initializes Git, leaks URL credentials, executes project module
  shadows, overwrites existing named hooks, removes unverified instructions, changes an
  existing Git policy, or rewrites active product checks.
- **Red observed before green:** yes; each listed preservation/privacy failure was
  reproduced against the earlier wrapper/source behavior before its regression turned green.
- **Confidence:** [Verified] on Linux and [Flagged] pending actual final GitHub-hosted
  Linux/macOS/Windows matrix readback.
- **Residual risk:** selected source is trusted executable code; cooperative drift
  detection is not a concurrent-writer lock or a power-loss transaction. Unsafe legacy
  transformations deliberately stop for reconciliation rather than guess ownership.

### Claim 3: the installed entry point can complete a real small task and resume interruptions
- **Evidence:** an installed `/deliver` skill in GitHub Copilot CLI grounded a README-only
  T0 correction, stopped when a required command permission was unavailable, resumed the
  same task after permission was supplied, survived one transient model connection timeout,
  changed the exact requested bytes, and passed the unchanged verifier. No owned audit log
  or product graph was created.
- **Oracle:** a pre-existing verifier was observed red before the task and its original
  SHA-256 was read back after completion; exact README bytes were asserted separately.
- **Red observed before green:** yes.
- **Confidence:** [Verified] for this one installed native scenario.
- **Residual risk:** this is not proof for every host/model/backend. The host's ignored
  session-start timing marker is inherited runtime plumbing, not an authored audit entry.

## Boundary coverage

| Boundary | Evidence |
|---|---|
| Empty request / review-only request | skill contract and reference tests |
| T0 proportional path / T1-T2 reviewed paths | route + checkpoint CLI tests |
| Defect, migration, UI, architecture, coordination | route matrix and ordered transition tests |
| Human decision, permission, veto, release | bound positive/negative receipt controls |
| Plain project, Git root, linked worktree, subdirectory | bootstrap/checkpoint integration tests |
| Dirty/untracked work, local policy, generated product data | preservation and conflict-refusal probes |
| Symlink, hardlink, FIFO, directory conflict, Windows reparse | path-safety fixtures; native junction remains matrix evidence |
| Initial/repeat/preview/unknown ref/hidden commit/I/O failure | bootstrap CLI tests and committed-source fixtures |
| UTF-8/legacy console/cross-shell command shape | portability gates and native shell workflow |
| Evaluator tampering / early exit / final-state mutation | trusted pre/behavior/post oracle assertions |

## Failure modes addressed

- Conditional routing does not become a blind all-skills conveyor belt.
- Checkpoint transport, model completion or matching JSON structure are not acceptance.
- Unanswered/denied/stale/wrong-author decisions do not become consent.
- A remote wrapper cannot silently substitute `main` for an unresolved requested ref.
- Product policy and safety checks are not treated as disposable because their filenames
  once belonged to the pack.
- Project modules cannot shadow stdlib imports during a no-write bootstrap preview.
- Worker-writable verifiers cannot approve an unimplemented or prematurely exiting product.

## Final acceptance readback

- The complete local bundle finished with **1,500 passed, 42 skipped and 833
  subtests passed**; all **18/18** consistency, portability, source-sync,
  Python, Node, graph, doctor, eval-shape and budget gates passed.
- The complete local Playwright result on the final artifact set is **264 passed,
  12 deliberately skipped** across Chromium, Firefox and WebKit.

- **Qualified implementation commit:** `049d234b5e64cd8fd04d354c071c6ec99aaffab3`,
  authored as `Alex Hutanu <alex@hutanu.net>`.
- **Native matrix:** [GitHub Actions run 37055642430](https://github.com/ahutanu/ai-forward/actions/runs/37055642430)
  completed successfully for Ubuntu, macOS and Windows on that exact SHA.
- Every platform passed routing/resume/preservation/deployment tests and an actual
  HTTPS exact-SHA one-line install plus repeat install in a plain project. Windows
  additionally passed the exact `cmd.exe` one-liner and native junction fixture.
- A separate public exact-SHA smoke retained dirty product bytes, initialized no Git
  repository, installed revision 98, and repeated byte-identically.
