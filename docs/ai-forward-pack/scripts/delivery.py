#!/usr/bin/env python3
"""Conditional delivery routing and local checkpoint integrity, not a workflow runner."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile
from typing import Any, cast

# PLAT-A: direct routes/refusals must not depend on compiler imports to configure stdio.
for _stream in (sys.stdout, sys.stderr):
    _reconfigure = getattr(_stream, "reconfigure", None)
    if callable(_reconfigure):
        try:
            cast(Any, _stream).reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass


def route(facts):
    required = {"kind", "tier", "questions", "risks", "ui", "coordination"}
    risks = {"security", "identity", "data", "contracts", "money", "concurrency"}
    if (not isinstance(facts, dict) or not required <= set(facts) or set(facts) - required - {"design_ready"}
            or facts["kind"] not in ("feature", "defect", "migration", "docs")
            or facts["tier"] not in ("T0", "T1", "T2")
            or type(facts.get("design_ready", False)) is not bool
            or type(facts["ui"]) is not bool or type(facts["coordination"]) is not bool
            or not isinstance(facts["questions"], list) or not isinstance(facts["risks"], list)
            or any(q not in ("requirements", "architecture", "design") for q in facts["questions"])
            or any(not isinstance(r, str) or r not in risks for r in facts["risks"])):
        raise ValueError("invalid facts: use the documented closed routing schema")
    tier = "T2" if (facts["risks"] or facts["kind"] == "migration" or facts["coordination"]
                    or "architecture" in facts["questions"]) else facts["tier"]
    questions = list(facts["questions"])
    if (facts["risks"] or tier != "T0") and not facts.get("design_ready", False) and "design" not in questions:
        questions.append("design")
    stages = []
    for question, skill in (("requirements", "specify"), ("architecture", "define-architecture"),
                            ("design", "design-slice")):
        if question in questions:
            stages.append(skill)
    if facts["ui"]:
        stages.append("ui-design")
    if facts["kind"] == "defect":
        stages = ["investigate", "repair-review"] + stages
    implementation = {"feature": "implement", "defect": "implement", "migration": "migrate", "docs": "document"}
    if facts["coordination"]:
        if facts["kind"] == "migration":
            stages.append("migration-characterization")
        stages.extend(["prepare-for-coordination", "execute-with-coordination"])
    else:
        stages.append(implementation[facts["kind"]])
    stages.append("verify")
    return {"stages": stages, "tier": tier}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def git(repo, *args, optional=False):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, timeout=30)
    if result.returncode and not optional:
        raise ValueError("repository required: delivery needs a Git worktree")
    text = result.stdout.decode("utf-8") if not result.returncode else ""
    return text if "-z" in args else text.strip()


def identity(repo):
    repo = Path(repo).resolve()
    if not repo.is_dir():
        raise ValueError("project refused: --repo must name an existing directory")
    top = git(repo, "rev-parse", "--show-toplevel", optional=True)
    if not top:
        return {"root": str(repo), "kind": "plain"}
    root = Path(top).resolve()
    def absolute(value):
        return str((root / value).resolve())
    return {"root": str(root), "git_dir": absolute(git(root, "rev-parse", "--git-dir")),
            "common_dir": absolute(git(root, "rev-parse", "--git-common-dir"))}


def snapshot(repo, local_area=None):
    # Ignored/runtime inputs require explicit --input registration.
    project = identity(repo)
    repo = Path(project["root"])
    if project.get("kind") == "plain":
        names = []
        for directory, folders, files in os.walk(repo, followlinks=False):
            names.extend(str(Path(directory, name).relative_to(repo))
                         for name in folders if Path(directory, name).is_symlink())
            folders[:] = [name for name in folders
                          if name not in {".git", "node_modules", "__pycache__", ".venv", "venv"}
                          and not (local_area and Path(directory, name).is_relative_to(Path(local_area)))
                          and not Path(directory, name).is_symlink()]
            names.extend(str(Path(directory, name).relative_to(repo)) for name in files)
    else:
        names = git(repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard").split("\0")
    files = {}
    for name in sorted(set(filter(None, names))):
        path = Path(repo) / name
        if local_area and path.is_relative_to(Path(local_area)):
            continue
        if path.is_symlink():
            files[name] = {"link": os.readlink(path)}
        else:
            files[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return {"head": git(repo, "rev-parse", "HEAD", optional=True) if project.get("kind") != "plain" else "",
            "branch": git(repo, "symbolic-ref", "HEAD", optional=True) if project.get("kind") != "plain" else "",
            "files": digest(files)}


def file_record(path):
    path = Path(path).absolute()
    if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
        raise ValueError("evidence missing: supply a nonempty regular file")
    content = path.read_bytes()
    if not content.strip():
        raise ValueError("evidence missing: supply a nonempty regular file")
    return {"path": str(path), "sha256": hashlib.sha256(content).hexdigest()}


def check_records(records, label):
    for record in records:
        if (not isinstance(record, dict) or set(record) != {"path", "sha256"}
                or not isinstance(record["path"], str) or not record["path"]
                or not Path(record["path"]).is_absolute()
                or not isinstance(record["sha256"], str) or not re.fullmatch(r"[a-f0-9]{64}", record["sha256"])):
            raise ValueError("checkpoint refused: malformed file evidence record")
        try:
            current = file_record(record["path"])
        except (ValueError, OSError):
            raise ValueError(label + " drift: recorded file is missing") from None
        if current != record:
            raise ValueError(label + " drift: recorded file changed")


def compiler():
    spec = importlib.util.spec_from_file_location("delivery_compile", Path(__file__).with_name("prompt-compile.py"))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contract(audit_root, compiled_id):
    engine = compiler()
    entry = engine.find_entry(str(audit_root), compiled_id, "compilation")
    if not entry or entry.get("dispatchable") is not True or not isinstance(entry.get("compiled"), dict):
        raise ValueError("contract refused: use a finished dispatchable compilation id")
    doc = entry["compiled"]
    raw = engine.find_entry(str(audit_root), doc.get("raw_id"), "prompt")
    if not raw or engine.check_schema(doc) or engine._gate().verify_document(doc, raw["prompt"]):
        raise ValueError("contract refused: compiler provenance gate failed")
    if (doc.get("mode") == "not-compiled"
            or any(not isinstance(request, dict) or not isinstance(request.get("answer"), str)
                   or not request["answer"].strip() or request["answer"].strip().lower() == "unanswered"
                   for request in doc.get("decision_requests", []))):
        raise ValueError("contract refused: unresolved compiler decisions")
    return {"entry": entry, "raw_entry": raw}


def local_area(repo, state_root=None):
    project = identity(repo)
    if state_root is not None:
        requested = Path(state_root)
        area = requested.resolve()
        if requested.is_symlink() or Path(project["root"]).is_relative_to(area):
            raise ValueError("state path refused: choose a dedicated nonsymlink local area, not the project or its ancestor")
        return area
    if "git_dir" in project:
        return Path(project["git_dir"]) / "ai-forward/delivery"
    home = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state")
    return home / "ai-forward/delivery"


def state_path(repo, task, state_root=None):
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", task):
        raise ValueError("invalid task: use a lowercase slug, at most 64 characters")
    project = identity(repo)
    area = local_area(repo, state_root)
    if state_root is not None or project.get("kind") == "plain":
        area = area / digest(project)
    return area / (task + ".json")


def save(path, state):
    state["integrity"] = digest({k: v for k, v in state.items() if k != "integrity"})
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
        temporary = handle.name
    os.replace(temporary, path)


def view(state):
    done = len(state["completed"])
    return {**state, "next": state["stages"][done] if done < len(state["stages"]) else None}


def load(repo, task, check_tree=True, state_root=None):
    path = state_path(repo, task, state_root)
    state = read_json(path)
    if (not isinstance(state, dict) or state.get("version") != 2
            or state.get("integrity") != digest({k: v for k, v in state.items() if k != "integrity"})):
        raise ValueError("checkpoint refused: corrupt or unsupported checkpoint; do not infer progress")
    try:
        selected = route(state["facts"])
        valid = (all(isinstance(state[k], str) and state[k].strip() for k in ("task", "audit_root", "compiled_id", "raw"))
                 and isinstance(state["identity"], dict) and isinstance(state["contract"], dict)
                 and isinstance(state["snapshot"], dict)
                 and all(isinstance(state[k], list) for k in ("stages", "inputs", "completed", "partial", "decisions"))
                 and state["stages"] == selected["stages"] and state["tier"] == selected["tier"])
        if not valid:
            raise ValueError("shape")
        for record in state["inputs"]:
            if (not isinstance(record, dict) or not isinstance(record.get("path"), str)
                    or not record["path"] or not isinstance(record.get("sha256"), str)):
                raise ValueError("input record")
        for completed in state["completed"]:
            if (not isinstance(completed, dict) or not isinstance(completed.get("stage"), str)
                    or not isinstance(completed.get("actor"), str) or not completed["actor"].strip()
                    or not isinstance(completed.get("evidence"), list) or not completed["evidence"]):
                raise ValueError("stage record")
        if [row["stage"] for row in state["completed"]] != state["stages"][:len(state["completed"])]:
            raise ValueError("stage order")
        for partial in state["partial"]:
            if (not isinstance(partial, dict) or set(partial) != {"stage", "actor", "evidence"}
                    or partial["stage"] not in state["stages"][:len(state["completed"]) + 1]
                    or not isinstance(partial["actor"], str) or not partial["actor"].strip()
                    or not isinstance(partial["evidence"], list)):
                raise ValueError("partial author record")
        for record in state["decisions"]:
            if not isinstance(record, dict) or not isinstance(record.get("evidence"), list) or not record["evidence"]:
                raise ValueError("decision record")
        gate = state["gate"]
        if gate is not None and (not isinstance(gate, dict) or gate.get("authority") not in ("human", "reviewer")
                or gate.get("kind") not in ("decision", "permission", "hard-veto", "release")
                or any(not isinstance(gate.get(k), str) or not gate[k].strip() for k in ("id", "binding", "question", "stage"))
                or not isinstance(gate.get("evidence"), list)):
            raise ValueError("gate record")
    except (ValueError, TypeError, KeyError):
        raise ValueError("checkpoint refused: malformed routing or progress records; do not infer progress") from None
    if (state["task"] != task or state["identity"] != identity(repo)
            or state.get("local_area", str(local_area(repo, state_root))) != str(local_area(repo, state_root))):
        raise ValueError("identity drift: checkpoint belongs to a different task or worktree")
    if contract(state["audit_root"], state["compiled_id"]) != state["contract"]:
        raise ValueError("contract drift: re-ground and request a new accepted contract")
    check_records(state["inputs"], "input")
    for completed in state["completed"] + state["partial"] + state["decisions"]:
        check_records(completed["evidence"], "evidence")
    if state["gate"]:
        check_records(state["gate"]["evidence"], "evidence")
    if check_tree and snapshot(state["identity"]["root"], state.get("local_area")) != state["snapshot"]:
        raise ValueError("input drift: workspace changed since the checkpoint")
    return path, state


def new_gate(state, kind, authority, question):
    binding = digest({"identity": state["identity"], "task": state["task"],
                      "contract": state["contract"], "snapshot": state["snapshot"],
                      "completed": state["completed"], "partial": state["partial"]})
    return {"id": secrets.token_hex(16), "kind": kind, "authority": authority,
            "question": question, "binding": binding, "stage": view(state)["next"], "evidence": []}


def resume(state, receipt_path):
    gate = state["gate"]
    receipt = read_json(receipt_path)
    if (not gate or not isinstance(receipt, dict)
            or receipt.get("task") != state["task"] or receipt.get("gate") != gate["id"]
            or receipt.get("binding") != gate["binding"] or receipt.get("authority") != gate["authority"]
            or receipt.get("decision") != "approved"
            or not isinstance(receipt.get("actor"), str) or not receipt["actor"].strip()
            or not isinstance(receipt.get("evidence"), str) or not receipt["evidence"].strip()
            or receipt.get("source") != {"human": "human-message", "reviewer": "reviewer-report"}[gate["authority"]]):
        raise ValueError("decision refused: need explicit approval from the gate's authority, bound to this checkpoint")
    if gate["authority"] == "reviewer" and receipt["actor"] in {r["actor"] for r in state["completed"] + state["partial"]}:
        raise ValueError("decision refused: author cannot clear their own hard veto")
    records = [file_record(receipt_path), file_record(receipt["evidence"])] + gate["evidence"]
    state["decisions"].append({"gate": gate, "receipt": receipt, "evidence": records})
    if gate["stage"] == "repair-review":
        state["completed"].append({"stage": "repair-review", "actor": receipt["actor"], "evidence": records})
    state["gate"] = None


def close_outcome(state, path):
    if path is None:
        raise ValueError("closure refused: map every original criterion to real-path evidence")
    report = read_json(path)
    required = {"criteria", "changes", "tests", "skips", "limits", "remaining_gates"}
    original = state["contract"]["entry"]["compiled"]["goal_state"]["done_when"]
    if (not isinstance(report, dict) or set(report) != required
            or any(not isinstance(report[k], list) for k in required)
            or report["remaining_gates"]
            or any(not isinstance(row, dict) for row in report["criteria"])
            or [row.get("criterion") for row in report["criteria"]] != original):
        raise ValueError("closure refused: original criteria must match exactly; remaining gates cannot be closed")
    records = [file_record(path)]
    for row in report["criteria"]:
        if (not isinstance(row.get("observed"), str) or not row["observed"].strip()
                or not isinstance(row.get("evidence"), list) or not row["evidence"]
                or any(not isinstance(p, str) or not p.strip() for p in row["evidence"])):
            raise ValueError("closure refused: each criterion needs observations and evidence")
        records.extend(file_record(p) for p in row["evidence"])
    return report, records


def execute(args):
    if args.verb == "route":
        return route(read_json(args.facts))
    if args.verb == "start":
        path = state_path(args.repo, args.task, args.state_root)
        if path.exists():
            raise ValueError("task exists: resume it instead of overwriting completed work")
        facts = read_json(args.facts)
        accepted = contract(args.audit_root, args.compiled_id)
        compiled_tier = accepted["entry"]["compiled"]["goal_state"]["tier"]
        if compiled_tier not in ("T0", "T1", "T2"):
            raise ValueError("contract refused: unknown cost-of-error tier")
        route(facts)  # Validate caller input before applying the higher safety floor.
        facts["tier"] = max(facts["tier"], compiled_tier)
        selected = route(facts)
        area = str(local_area(args.repo, args.state_root))
        state = {"version": 2, "task": args.task, "identity": identity(args.repo), "local_area": area,
                 "audit_root": str(args.audit_root.resolve()), "compiled_id": args.compiled_id,
                 "contract": accepted, "raw": accepted["raw_entry"]["prompt"], "facts": facts,
                 **selected, "completed": [], "partial": [], "gate": None, "decisions": [],
                 "inputs": [file_record(p) for p in [args.facts, *args.input]],
                 "snapshot": snapshot(args.repo, area)}
        save(path, state)
        return view(state)
    path, state = load(args.repo, args.task, check_tree=args.verb not in ("complete", "pause"), state_root=args.state_root)
    if args.verb == "complete":
        if state["gate"] or view(state)["next"] != args.stage or not args.actor.strip():
            raise ValueError("stage refused: complete only the current ungated stage")
        records = [file_record(p) for p in args.evidence]
        if args.stage == "verify":
            state["closure"], closure_records = close_outcome(state, args.closure)
            records.extend(closure_records)
        state["completed"].append({"stage": args.stage, "actor": args.actor, "evidence": records})
        state["snapshot"] = snapshot(args.repo, state.get("local_area"))
        trivial = (state["tier"] == "T0" and not state["facts"]["ui"]
                   and not state["facts"]["coordination"])
        if args.stage in ("implement", "migrate", "document", "execute-with-coordination") and not trivial:
            state["gate"] = new_gate(state, "hard-veto", "reviewer", "Independent applicable reviewer: clear the exit checklist with evidence, or BLOCK")
        if view(state)["next"] == "repair-review":
            state["gate"] = new_gate(state, "decision", "human", "Approve the diagnosed repair phases (or provide explicit prior human authorization)?")
        save(path, state)
    elif args.verb == "pause":
        expected = "reviewer" if args.kind == "hard-veto" else "human"
        if state["gate"] or view(state)["next"] is None or not args.question.strip() or args.authority != expected:
            raise ValueError("gate refused: need an active ungated task and a specific question")
        current = snapshot(args.repo, state.get("local_area"))
        records = [file_record(p) for p in args.evidence]
        if current != state["snapshot"] and not records:
            raise ValueError("gate refused: changed in-progress work requires partial-work evidence")
        if ((records or args.kind == "hard-veto") and not args.actor
                or any(not actor.strip() for actor in args.actor)):
            raise ValueError("gate refused: record actual stage authors with --actor for partial work or a hard veto")
        state["partial"].extend({"stage": view(state)["next"], "actor": actor, "evidence": records}
                                for actor in dict.fromkeys(args.actor))
        state["snapshot"] = current
        state["gate"] = new_gate(state, args.kind, args.authority, args.question)
        state["gate"]["evidence"] = records
        save(path, state)
    elif args.verb == "resume":
        resume(state, args.receipt)
        save(path, state)
    return view(state)


def locked_execute(args):
    if args.verb in ("route", "status"):
        return execute(args)
    path = state_path(args.repo, args.task, args.state_root).with_suffix(".lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("checkpoint busy: another writer or interrupted operation holds the lock") from None
    try:
        os.close(descriptor)
        return execute(args)
    finally:
        path.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="verb", required=True)
    for verb in ("route", "start", "status", "complete", "pause", "resume"):
        command = commands.add_parser(verb)
        if verb in ("route", "start"):
            command.add_argument("--facts", type=Path, required=True)
        if verb != "route":
            command.add_argument("--repo", type=Path, default=Path.cwd())
            command.add_argument("--state-root", type=Path)
            command.add_argument("--task", required=True)
        if verb == "start":
            command.add_argument("--audit-root", type=Path, required=True)
            command.add_argument("--compiled-id", required=True)
            command.add_argument("--input", type=Path, action="append", default=[])
        if verb == "complete":
            command.add_argument("--stage", required=True)
            command.add_argument("--closure", type=Path)
            command.add_argument("--actor", required=True)
            command.add_argument("--evidence", type=Path, action="append", required=True)
        if verb == "pause":
            command.add_argument("--kind", choices=("decision", "permission", "hard-veto", "release"), required=True)
            command.add_argument("--authority", choices=("human", "reviewer"), required=True)
            command.add_argument("--question", required=True)
            command.add_argument("--actor", action="append", default=[])
            command.add_argument("--evidence", type=Path, action="append", default=[])
        if verb == "resume":
            command.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(locked_execute(args), ensure_ascii=False))
    except (ValueError, OSError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
