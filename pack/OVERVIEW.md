# AI-Forward Pack — Overview

Use this page to understand the installed files and choose an individual workflow
when you want more control. For most tasks, install once and use `deliver`: the
agent chooses the needed stages while keeping your original outcome in view.
For the pack's purpose and limits, read [`README.md`](README.md).

AI-Forward supports **Claude Code**, **GitHub Copilot**, **Grok Build**,
**Antigravity** and **Codex**. Its foundational knowledge documents are included;
you do not need a separate Agent Knowledge Pack installation.

## 1. Install in your project

Open a terminal in the project you want to work on. You need Git,
[uv](https://docs.astral.sh/uv/getting-started/installation/), network access and a
supported coding app with its own account/model access. Git repositories and plain
projects are supported; you do not need to clone AI-Forward first.

**Available now: the fork preview, not an upstream release.** Copy this one line:

```text
uv run --no-config --no-project --script https://raw.githubusercontent.com/ahutanu/ai-forward/feat/one-command-adoption/bootstrap.py --repo https://github.com/ahutanu/ai-forward.git --ref feat/one-command-adoption
```

It works in Windows PowerShell/Command Prompt and macOS/Linux terminals, with Git
and uv on PATH. Setup reports `AI-Forward installed`, `AI-Forward updated` or
`AI-Forward already current`, with the revision and exact source commit. These
messages describe installation, not a completed project task.

- Append `--dry-run` to see the plan without project writes.
- Rerun the line to check or update the installed pack.
- For a pinned version, use the same full commit id in both the wrapper URL and
  `--ref`; a branch can move.
- `--source <clone-path>` uses an existing local Git clone's committed HEAD,
  not its uncommitted edits.

Setup does not initialize Git, install project dependencies, commit, push, deploy
or change model/trust permissions. If existing instructions, hooks, Git settings or
checks conflict, it names the item and stops for review. Preserve the existing
file and reconcile the specific conflict. A successful install is not a reason to
enable broad permissions.

## 2. Ask for a result

Open the project in your coding app and start a fresh chat:

| App | Invocation |
|---|---|
| Claude Code | `/deliver <your task>` |
| Codex | `$deliver <your task>` |
| Copilot CLI | Find `deliver` with `/skills`, then `/deliver <your task>`; you can also ask `Use the /deliver skill to <your task>`. If needed, `/skills reload`, then `/skills info deliver`. |
| VS Code Copilot | `/deliver` when listed, or select/request the installed `deliver` skill; Agent Host sessions use skills rather than older prompt files |
| Grok Build / Antigravity | Select or request the installed `deliver` skill by name |

These are chat requests, not terminal commands. Give the intended result, a
checkable finish line and what must stay unchanged:

```text
/deliver Add CSV export for the active project and filter. Export every matching task, not only the visible page. Do not add scheduling or new roles.
```

`deliver` selects only the applicable workflows, reuses valid existing work and
continues between approved stages. It does not run the whole catalog, adopt your
entire repository or spawn a team by default. Shortening the route must not drop
an acceptance condition, safety check or required review.

If work pauses, the agent explains the question and gives you a task id. Reply in
the same chat, or use `/deliver resume <task-id>` in a fresh chat in the same project
(Codex: `$deliver resume <task-id>`; Copilot CLI: request the `/deliver` skill to
resume that id). The request, project and saved evidence are checked before valid
work is reused. Checkpoints are local, not automatically shared across clones.
Your reply answers only that decision; it does not grant unrelated permissions.
Blocking review findings must be addressed and independently re-reviewed, not
self-approved.

## 3. Understand the installed files

The usual install supplies the supported host surfaces together:

```text
<project>/
├─ CLAUDE.md / AGENTS.md             # managed instructions alongside your content
├─ .claude/                          # knowledge, skills and personas
├─ .github/                          # Copilot instructions, prompts and personas
├─ .grok/                            # Grok skills, personas, hooks and rules
├─ .agents/                          # shared skills for Codex/Antigravity and host wiring
└─ docs/ai-forward-pack/              # pack guides, templates and local scripts
```

The exact file map is in `adapters/INSTALL.md` in the bundle,
or `docs/ai-forward-pack/INSTALL.md` after installation. Host discovery differs:
Copilot's prompt-file route is not the same as its CLI/Agent Host skill route;
Codex discovers `.agents/skills/` and reads project instructions from `AGENTS.md`.
Check the relevant host guide when discovery fails rather than copying files at
random. The installed Codex guide is `docs/ai-forward-pack/codex.md`.

Presence of these files does not prove that the running app loaded them or obeyed
a hook. Ask the agent to identify the installed skill it would use. The installed
`pack-doctor.py` checks file-level readiness; it is not a live model or permission
test. The delivery helper checks local progress records, not the meaning of the
result or the authenticity of human consent.

## 4. Choose a specific workflow when you need one

You do not need to memorize this table before using `deliver`. It is here when you
want a diagnosis, design or review as the outcome rather than a completed change.
In Codex, use the `$` form; in apps without a listed slash command, request the
installed skill by name.

| Need | Skill | What to inspect |
|---|---|---|
| Explore an idea | `/create-proposal` | Options and questions before requirements are fixed |
| Understand an unfamiliar domain | `/collectknowledge` | Sources, uncertainty and vocabulary relevant to the problem |
| Add relevant subject expertise | `/adddomainexperts` | Proposed project-specific lenses before approving the set |
| Define new behavior | `/specify` | Testable requirements, user experience and explicit exclusions |
| Change system boundaries | `/define-architecture` | Contracts, alternatives, consequences and delivery slices |
| Design a component | `/design-slice` | Inputs, outputs, failure cases and a verification plan |
| Settle an interface before building | `/ui-design` | Flows, states, accessibility and visual design |
| Build an understood change | `/implement` | Code and red→green→refactor evidence through the real path |
| Find why behavior is wrong | `/investigate` | Demonstrated cause and repair proposal; then your repair decision |
| Upgrade or refactor | `/migrate` | Old behavior characterized first, intended differences and rollback |
| Map an existing project | `/adopt` | Recovered architecture and useful existing knowledge—not a mandatory setup step |
| Assess an existing system | `/forensicreview` | Evidence-linked risks and a prioritized backlog; no production repair |
| Review or repair code hygiene | `/code-hygiene` | Findings and, when authorized, tested remediation |
| Split justified independent work | `/prepare-for-coordination`, then `/execute-with-coordination` | Ownership, contracts, limits and integrated outcome evidence |
| Keep documentation useful | `/document` | What was actually built, its limits and current relationships |

A question or review-only request authorizes analysis, not product changes.
Investigation is not permission to implement its repair. `deliver` retains that
repair-review pause unless your actual prior instruction explicitly authorized the
diagnosed repair. A migration must preserve characterization; an interface must
have its design settled before implementation. None of these workflows grants
permission to release or deploy.

## 5. Read the handback against the request

The important comparison is the original finish line against observed behavior.
For CSV export, a page of 20 rows and 63 matching tasks must yield all 63 matches
while excluding other projects. A serializer unit test alone cannot establish that.
Ask for the real query-to-download check, the changed files and any untested limits.

A useful status separates **Completed**, **Remaining** and **Best next action**.
If a criterion is unmet or a gate is unanswered, the task is still open. An agent's
success message, a checkpoint hash or a passing test is not acceptance by itself.

## 6. Go deeper only as needed

In the source bundle, the standards below are under `knowledge/`; in an installed
project, they are under `.claude/knowledge/` (shared across hosts).

- **Reasoning and review:** `rigor-protocol.md`, `collaborative-personas.md` and
  `persona-cards.md`. Personas are specialist viewpoints, not a default swarm;
  authors do not clear their own hard vetoes.
- **Requirements and evidence:** `specification-standards.md` and
  `end-to-end-integrity.md`.
- **Installation or updates:** `adapters/INSTALL.md` in the bundle, or
  `docs/ai-forward-pack/INSTALL.md` in the installed project. Manual reconciliation
  and `/addpacktorepo` or `/updatepack` are expert alternatives to the one-line
  setup, not extra onboarding steps.
- **Records and continuity:** `/auditlog`, `/prompts` and `/searchprompts` read prior
  work; `/also` queues a late addition without silently replacing current scope.
- **Learning or extending the pack:** `/dream` proposes learning, `/apply-learnings`
  reconciles approved learning, and `/extendaibundle` changes the pack when requested.
- **Design rationale:** [`research-synthesis.md`](research-synthesis.md).

The source bundle is organized as `commands/`, `knowledge/`, `templates/`,
`adapters/`, `scripts/`, `evals/` and `examples/`. The foundational knowledge pack is
vendored in `knowledge/`; no prior installation is assumed. The
[public handbook](https://timianmalloo.github.io/ai-forward/docs/portal/index.html)
is the upstream edition; preview-only changes may not be published there yet.
