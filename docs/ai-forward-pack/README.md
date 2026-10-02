# The AI-Forward Pack

AI-Forward gives AI coding tools a shared set of project instructions, workflows
and review standards. Describe the result you want; the agent reads your project,
chooses the needed work and checks the result against your request. Important
decisions come back to you. The aim is evidence you can review, not just a confident
completion message.

It works with **Claude Code**, **GitHub Copilot**, **Grok Build**, **Antigravity**
and **Codex**. You can use an existing Git repository or a plain project; it does
not have to be hosted on GitHub. The pack includes its foundational knowledge
documents, so you do not need another knowledge-pack installation first.

## Start here

You need Git, [uv](https://docs.astral.sh/uv/getting-started/installation/), network
access and a supported coding app with its own account/model access.
**This contribution is a fork preview, not an upstream release.** Open a terminal
in the project you want to work on and copy this one line:

```text
uv run --no-config --no-project --script https://raw.githubusercontent.com/ahutanu/ai-forward/feat/one-command-adoption/bootstrap.py --repo https://github.com/ahutanu/ai-forward.git --ref feat/one-command-adoption
```

The line works in Windows PowerShell/Command Prompt and macOS/Linux terminals,
with Git and uv on PATH. Setup reports `AI-Forward installed`, `AI-Forward updated`
or `AI-Forward already current`, with the revision and exact source commit.
Open that project in your coding app and start a fresh chat.

- **Claude Code / apps with the installed slash entry point:** `/deliver <your task>`.
- **Codex:** `$deliver <your task>`.
- **Copilot CLI:** find `deliver` with `/skills`, then use `/deliver <your task>`.
  You can also ask `Use the /deliver skill to <your task>`. If installed during a
  chat, use `/skills reload`, then `/skills info deliver`.
- **VS Code Copilot:** use `/deliver` when listed, or select/request the installed
  `deliver` skill. Agent Host sessions use skills rather than the older prompt files.
- **Grok Build / Antigravity:** select or request the installed `deliver` skill by name.

These are chat requests, not shell commands. For example:

```text
/deliver Add CSV export for the active project and filter. Export every matching task, not only the visible page. Do not add scheduling or new roles.
```

Replace the example with a change in your project. Say what correct behavior looks
like and what must stay unchanged. You do not need to choose each stage yourself.

## What delivery means

`deliver` selects only the work the outcome needs. A small, understood change can
take a short path. A defect needs a demonstrated cause and a repair decision; a
migration needs evidence of old behavior before changing it; an interface needs its
design settled before building. Required checks do not disappear because the diff
is small. No team is spawned by default.

The agent may change its implementation approach, but not quietly change your
requirements to make the result pass. If 63 tasks match a filter but the page shows
20, exporting the visible 20 is a different outcome—not a simpler way to finish.
The checks need to exercise the actual query-to-download path and project boundary.

A useful handback identifies:

- what changed and where to inspect it;
- how each original completion condition was checked;
- which checks ran, what they returned and what did not run;
- remaining decisions, limits or blockers.

A plan, a generated document, a passing unit test or a worker's success message is
not enough on its own. Installation makes the pack available; completion still
needs evidence of the requested result.

## When work pauses

A pause keeps the task open. The agent explains what is blocked, asks a specific
question and gives you a task id. Reply in the same chat. Approval applies only to
the decision you answered; it does not grant unrelated tool access or permission to
release. A blocking review needs the finding addressed and independently
re-reviewed; the author cannot clear its own veto.

In a fresh chat in the same project, use `/deliver resume <task-id>` (Codex:
`$deliver resume <task-id>`). In Copilot CLI, ask it to use the `/deliver` skill to
resume that id. The agent checks the request, project and evidence before reusing
valid work. Changed or missing inputs require an explanation and revalidation, not
an invented approval or a silent reset. Checkpoints are local, not automatically
shared with another clone or computer.

The local helper records and checks progress. It does not run the coding workflows,
authenticate people or judge the meaning of a result. Your coding agent and you
still need to inspect the actual evidence.

## What is inside

| Part | What it helps with |
|---|---|
| **Skills** in `commands/` | Repeatable workflows for planning, building, checking, documenting and continuing work |
| **Knowledge** in `knowledge/` | Standards for requirements, contracts, testing, interfaces and outcome ownership |
| **Personas** in `adapters/` | Specialist authoring and review lenses selected when relevant—not a permanently running swarm |
| **Templates** in `templates/` | Useful starting shapes for specifications, designs, investigations and proof |
| **Scripts** in `scripts/` | Deterministic local mechanics for installation, records, checkpoints and other supported tasks |
| **Regression cases** in `evals/` | Checks of specific workflow behavior; not a guarantee about every model or coding app |

The reasoning discipline is simple: understand the problem, inspect the relevant
contracts, establish evidence, try to find the flaw, then say only what the evidence
supports. Unfamiliar APIs should be checked in source or a small working experiment,
not filled in from memory. Specialist review should challenge the work, not merely
repeat the author's conclusion.

A persona is a viewpoint, not necessarily a separate process. It can help author a
proposal or challenge one; a hard veto still needs independent clearance. Human
permission remains separate from model review. More roles or more documents are
not the goal.

## Setup and updates without surprises

The one-line setup above uses the existing deployment map and checks installed
files. Append `--dry-run` to preview without writing to the project. Rerun it to
check or update the installed pack. To pin a version, use the same full commit id
in the wrapper URL and `--ref`; a branch can move.

Setup does not initialize Git, install project dependencies, commit, push, deploy
or change model/trust permissions. If instructions, hooks, Git settings or checks
conflict, it names the item and stops for review. Keep the existing file and
reconcile the specific conflict rather than deleting project policy or granting
blanket permissions. Use a credential-free repository URL with Git's credential
helper, not a token in a URL.

Manual reconciliation is an expert alternative, not a required extra step. Its
file-by-file map and revision changelog are in `adapters/INSTALL.md` in this bundle
and `docs/ai-forward-pack/INSTALL.md` after installation. The base knowledge pack
is included; local project rules still need to be preserved and reconciled.

## Where to go next

- **Try one task:** use `deliver`, inspect the result and keep any pause id.
- **Understand the files or choose a stage:** read [`OVERVIEW.md`](OVERVIEW.md).
- **Read the reasoning standards:** start with `rigor-protocol.md` in the bundle's
  `knowledge/` directory or the installed project's `.claude/knowledge/` directory.
- **Review an install conflict:** use `adapters/INSTALL.md` in the bundle or
  `docs/ai-forward-pack/INSTALL.md` in the installed project.
- **See the research behind the design:** read [`research-synthesis.md`](research-synthesis.md).

In the AI-Forward source repository, the full reader handbook is built from
`web/handbook/` into `docs/portal/index.html`. The
[public handbook](https://timianmalloo.github.io/ai-forward/docs/portal/index.html)
is the upstream edition and may not include this fork preview yet. Codex's installed
setup guide is `docs/ai-forward-pack/codex.md`; its bundle source is
`adapters/codex/codex.md`.
