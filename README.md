# AI-Forward

Project instructions, workflows and review standards for AI coding tools. Describe
the result you want; the agent reads your project, chooses the needed work and
checks the result against your request. Important decisions come back to you.
The aim is a result you can verify, not just a plausible completion message.

AI-Forward works with **Claude Code**, **GitHub Copilot**, **Grok Build**,
**Antigravity** and **Codex**. It is a pack of files installed in your project,
not a hosted service or a model. Your coding app supplies model access and tools.

## Start with one outcome

Install once, then describe the result you want. You do not need to clone AI-Forward
or learn its workflow sequence first. Start with a small change you can review.

**This branch is a fork preview, not an upstream release.** The command below uses
the preview. You need [Git](https://git-scm.com/downloads),
[uv](https://docs.astral.sh/uv/getting-started/installation/), network access and a
supported coding app with its own account/model access.

### 1. Install in your project

Open a terminal in the project you want to work on, then copy this one line. It works
in Windows PowerShell/Command Prompt and macOS/Linux terminals, with Git and uv on
PATH. A project without Git is welcome too; setup will not initialize it for you.

```text
uv run --no-config --no-project --script https://raw.githubusercontent.com/ahutanu/ai-forward/feat/one-command-adoption/bootstrap.py --repo https://github.com/ahutanu/ai-forward.git --ref feat/one-command-adoption
```

Success reports `AI-Forward installed`, `AI-Forward updated` or
`AI-Forward already current`, with the revision and exact source commit. That means
the pack files are ready—not that a project task has been completed. Open this
project in your coding app and start a fresh chat so it can discover the new skill.

### 2. Ask for one result

In Claude Code or a coding app that exposes the installed `/deliver` entry point:

```text
/deliver Add CSV export for the current project and filter. Export every matching task, not only the visible page. Do not add scheduling or new roles.
```

This is a chat request, not a terminal command. Replace the example with a task in
your project. Say what correct behavior looks like and what must stay unchanged.

| Coding app | How to start |
|---|---|
| Claude Code | `/deliver <your task>` |
| Codex | `$deliver <your task>`; use `/skills` or `$` to find installed skills |
| Copilot CLI | Find `deliver` with `/skills`, then `/deliver <your task>`. You can also ask `Use the /deliver skill to <your task>`. If installed during a chat, use `/skills reload`, then `/skills info deliver`. |
| VS Code Copilot | Use `/deliver` when listed, or select/request the installed `deliver` skill. Agent Host sessions use skills, not the older prompt-file route. |
| Grok Build / Antigravity | Select or request the installed `deliver` skill by name using your app's skill support |

The agent chooses the needed workflows and continues through approved work. It does
not run every skill, map your entire repository or start a swarm by default.
Individual skills remain available when you want to direct a particular stage.

### 3. Review the result—or answer a necessary question

A useful handback shows changed files, checks that exercised your requested result,
any limits and any decision still needed. A plan or a passing test alone is not the
finish line. If 63 tasks match a filter but the page shows 20, the export must include
all 63. A test that serializes only the visible 20 does not prove that.

When a decision, permission or blocking review is needed, the agent explains what
is blocked, asks a specific question and saves its place with a task id. Reply in
the same chat. Your reply authorizes only the decision you actually answered; it
does not grant unrelated permissions or authorize deployment. A blocking review
requires the finding addressed and independently re-reviewed, not the author's own
approval.

In a fresh chat **in the same project**, use:

```text
/deliver resume <task-id>
```

Codex uses `$deliver resume <task-id>`; in Copilot CLI, ask it to use the `/deliver`
skill to resume that id. Replace `<task-id>` with the id the agent gave you.
The agent checks the saved request, project and evidence before reusing completed
work. If something changed, it explains what needs checking again rather than
silently starting over or inventing approval. Checkpoints are local; another clone
or computer does not automatically have them.

For a guided first task, read the [quick start](web/handbook/guides/get-started.md)
and [delivery guide](web/handbook/skills/deliver.md). Open `docs/portal/index.html`
locally for the searchable handbook built from this checkout.

### Setup options and safe stops

- **Preview:** append `--dry-run` to the setup line. It downloads/checks the source
  and shows the plan without writing to your project.
- **Repeat or update:** rerun the same line. Unchanged installed files stay current;
  newer source is reconciled against the installed version. Review the result.
- **Pin a version:** replace the branch in both the wrapper URL and `--ref` with
  the same full commit id. A branch can move; matching pins make a run reproducible.
- **Use local committed source:** `--source <clone-path>` uses a local Git clone's
  committed HEAD, not its uncommitted edits.

Setup does not change model/trust permissions, install project dependencies,
commit, push or deploy. If existing instructions, hooks, Git settings or checks
conflict, it stops and names the item for review. Keep the existing file and
reconcile the specific conflict; do not delete it or grant blanket permissions just
to make setup pass. Use a credential-free repository URL and Git's credential
helper, not a token in a URL.

Installing files is not proof that a model loaded or followed them. If `deliver`
is missing, check discovery before relying on it. The local progress helper checks
saved state; it does not authenticate a human decision or judge whether a result
meets the meaning of your request.

**After this contribution is merged and available upstream**, the shorter upstream
command will be:

```text
uv run --no-config --no-project --script https://raw.githubusercontent.com/timianmalloo/ai-forward/main/bootstrap.py
```

Until then, use the preview command above. Manual reconciliation and source-clone
installation are expert alternatives, not additional onboarding steps.

## Where to read next

- [Pack introduction](pack/README.md): what the pack helps with and what it does not promise.
- [Pack overview](pack/OVERVIEW.md): installed files and individual workflows.
- [Handbook source](web/handbook/): the reading journey, practical guides and every skill.
- [Public handbook](https://timianmalloo.github.io/ai-forward/docs/portal/index.html):
  the published upstream edition; fork-preview changes may not be there yet.
- [Codex setup](docs/ai-forward-pack/codex.md): discovery and troubleshooting.
- [Docs Explorer](docs/index.html): the project's linked architecture, decisions and records.

## Working on AI-Forward itself

This repository is both the development home of the pack and a project with the
pack already installed. In a clone, no separate adoption step is needed to work
on the pack. Change canonical source, then regenerate the installed copies.

```text
ai-forward/
├─ bootstrap.py           # portable setup entry point
├─ pack/                  # canonical pack source
│  ├─ commands/           # skills and their references
│  ├─ knowledge/          # project reasoning and review standards
│  ├─ templates/          # reusable artifact shapes
│  ├─ adapters/           # host wiring and INSTALL.md revision/changelog
│  ├─ scripts/            # deterministic local helpers
│  └─ evals/              # workflow regression cases
├─ web/handbook/          # canonical reader education
├─ tools/                 # sync, build and verification tools
├─ tests/                 # automated checks
├─ .claude/ .github/ .grok/ .agents/  # generated host installations
└─ docs/                  # project records plus generated pack/reader surfaces
```

`pack/` is authoritative for the pack; `web/handbook/` is authoritative for reader
education. Do not hand-edit generated skills, pack copies under
`docs/ai-forward-pack/`, or the generated reader. Project-owned records under
`docs/` are not all generated; follow their own source and ownership rules.

After an authorized pack change:

```powershell
pwsh tools/sync-pack.ps1
pwsh -NoProfile -File tools/verify-bundle.ps1
```

Review the regenerated surfaces and the real verification output. Update the pack
revision/changelog in `pack/adapters/INSTALL.md` according to its maintenance
policy, and include canonical and affected generated files in the same change.
Use the relevant tests and, where needed, a real coding-app exercise; a file-level
check does not establish model compliance.

To build a shareable bundle:

```powershell
pwsh tools/package-pack.ps1
```

This writes `dist/ai-forward-pack.zip`. The deployment map and expert reconciliation
procedure are in [INSTALL.md](pack/adapters/INSTALL.md). Packaging does not install,
release or publish the bundle.

## License

[Apache-2.0](LICENSE).
