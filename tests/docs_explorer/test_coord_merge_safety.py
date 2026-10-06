"""Merge-safety controls from a consuming repo (x-harness-x-model-bench, 2026-10-05).

REG-C: a `register`-class merge driver applied to a non-JSONL file wrote "unreadable as JSONL;
not merging" with both sides between conflict markers and exited 0, so `git merge` auto-committed
the markers. The controls: `coord doctor` refuses a `register` entry on a non-`.jsonl` path, and
`merge-register` exits non-zero on input it cannot merge, so git stops with the path unmerged
(the markers stay in the file, so nothing looks clean).

ATTR-A: `coord install` added `merge=` lines and never removed the line of a pattern the registry
no longer declares; a file moved back to `authored` kept its old driver until a hand edit.

GATE-B (staged markers): a conflict-resolution edit failed while a parallel `git add` staged the
file, and the commit carried conflict markers. The control: the pre-commit floor and a
pre-merge-commit hook refuse staged conflict markers.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "pack" / "scripts" / "coord-core.py"
MARK = "<" * 7


def load_module():
    spec = importlib.util.spec_from_file_location("coord_core_merge_safety", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MergeSafetyCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name) / "r"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        self.git("config", "core.autocrlf", "false")

    def env(self):
        env = dict(os.environ)
        for key in ("COORD_ROOT", "AGENT_SESSION", "AGENT_NAME"):
            env.pop(key, None)
        return env

    def git(self, *args, check=True):
        return subprocess.run(["git", *args], cwd=str(self.repo), check=check, env=self.env(),
                              capture_output=True, text=True, encoding="utf-8", errors="replace")

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def commit_all(self, message):
        self.git("add", "-A")
        self.git("commit", "-qm", message)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=str(self.repo), env=self.env(),
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)


class RegisterClassTests(MergeSafetyCase):
    def test_doctor_refuses_a_register_entry_on_a_non_jsonl_path(self):
        self.write(".agents/artifacts.yml", "docs/notes/rulings.md: register\ndocs/audit/log.jsonl: register\n")
        self.commit_all("registry")
        out = self.cli("doctor").stdout
        self.assertIn("COORD-REGISTER-NOT-JSONL", out, "a markdown register is not refused")
        self.assertIn("docs/notes/rulings.md", out)
        self.assertNotIn("docs/audit/log.jsonl  ", out)

    def test_doctor_is_quiet_about_jsonl_registers(self):
        self.write(".agents/artifacts.yml", "docs/audit/*.jsonl: register\n")
        self.commit_all("registry")
        self.assertNotIn("COORD-REGISTER-NOT-JSONL", self.cli("doctor").stdout)

    def test_merge_register_exits_nonzero_on_unreadable_input_and_keeps_the_markers(self):
        m = load_module()
        ours, base, theirs = (self.repo / n for n in ("ours.md", "base.md", "theirs.md"))
        ours.write_text("# log\nours\n", encoding="utf-8")
        base.write_text("# log\n", encoding="utf-8")
        theirs.write_text("# log\ntheirs\n", encoding="utf-8")
        rc = m.cmd_merge_register(str(ours), str(base), str(theirs), "notes.md")
        self.assertNotEqual(0, rc, "exit 0 lets git auto-commit the marker file")
        self.assertIn(MARK, ours.read_text(encoding="utf-8"))

    def test_a_real_merge_of_a_markdown_register_stops_instead_of_committing_markers(self):
        self.write(".agents/artifacts.yml", "notes.md: register\n")
        self.write("notes.md", "# log\n")
        self.commit_all("base")
        installed = self.cli("install")
        self.assertEqual(0, installed.returncode, installed.stdout + installed.stderr)
        self.commit_all("attributes")
        trunk = self.git("symbolic-ref", "--short", "HEAD").stdout.strip()
        self.git("checkout", "-qb", "side")
        self.write("notes.md", "# log\nside entry\n")
        self.commit_all("side")
        self.git("checkout", "-q", trunk)
        self.write("notes.md", "# log\ntrunk entry\n")
        self.commit_all("trunk")
        head = self.git("rev-parse", "HEAD").stdout.strip()
        merged = self.git("merge", "--no-edit", "side", check=False)
        self.assertNotEqual(0, merged.returncode, "git merge auto-committed a register it could not merge")
        self.assertEqual(head, self.git("rev-parse", "HEAD").stdout.strip())
        self.assertIn(MARK, (self.repo / "notes.md").read_text(encoding="utf-8"))


class DerivedDriverTests(MergeSafetyCase):
    """REG-C's sibling: `merge-derived` on a path the registry does not classify `derived` wrote
    conflict markers and exited 0, so `git merge` auto-committed the markers (found 2026-10-05
    by the Lane F sweep of REG-C). The same treatment: keep the markers, exit 1."""

    def test_a_real_merge_of_an_authored_file_under_a_derived_pattern_stops(self):
        self.write(".agents/artifacts.yml",
                   "docs/gen/*: derived {} -c \"pass\"\ndocs/gen/hand.txt: authored\n".format(sys.executable))
        self.write("docs/gen/hand.txt", "base\n")
        self.commit_all("base")
        installed = self.cli("install")
        self.assertEqual(0, installed.returncode, installed.stdout + installed.stderr)
        self.assertIn("docs/gen/* merge=coord-regen",
                      (self.repo / ".gitattributes").read_text(encoding="utf-8").splitlines())
        self.commit_all("attributes")
        trunk = self.git("symbolic-ref", "--short", "HEAD").stdout.strip()
        self.git("checkout", "-qb", "side")
        self.write("docs/gen/hand.txt", "side edit\n")
        self.commit_all("side")
        self.git("checkout", "-q", trunk)
        self.write("docs/gen/hand.txt", "trunk edit\n")
        self.commit_all("trunk")
        head = self.git("rev-parse", "HEAD").stdout.strip()
        # --no-verify skips the pre-merge-commit staged-markers hook, so the driver's own exit
        # is the only control under test (the hook is the second line, GATE-B).
        merged = self.git("merge", "--no-edit", "--no-verify", "side", check=False)
        self.assertNotEqual(0, merged.returncode, "git merge auto-committed an authored file's conflict markers")
        self.assertEqual(head, self.git("rev-parse", "HEAD").stdout.strip())
        text = (self.repo / "docs/gen/hand.txt").read_text(encoding="utf-8")
        self.assertIn(MARK, text)
        self.assertIn("side edit", text, "theirs was discarded rather than surfaced")


class AttributesReconcileTests(MergeSafetyCase):
    def test_install_removes_merge_lines_the_registry_no_longer_declares(self):
        self.write(".agents/artifacts.yml", "docs/audit/*.jsonl: register\n")
        self.write(".gitattributes", "* text=auto eol=lf\n"
                                     "docs/notes/rulings.md merge=coord-register\n"
                                     "vendor/*.bin -text merge=coord-regen\n"
                                     "other.txt merge=somebody-else\n")
        self.commit_all("registry")
        installed = self.cli("install")
        self.assertEqual(0, installed.returncode, installed.stdout + installed.stderr)
        lines = (self.repo / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertNotIn("docs/notes/rulings.md merge=coord-register", lines, "a stale merge line survived")
        self.assertIn("vendor/*.bin -text", lines, "a stale coord driver token must go, its other attributes stay")
        self.assertIn("docs/audit/*.jsonl merge=coord-register", lines)
        self.assertIn("* text=auto eol=lf", lines)
        self.assertIn("other.txt merge=somebody-else", lines, "a driver install does not own is never touched")


class StagedMarkerTests(MergeSafetyCase):
    def test_the_precommit_floor_refuses_staged_conflict_markers(self):
        self.write("a.txt", "one\n")
        self.commit_all("base")
        self.write("a.txt", "one\n{} ours\ntwo\n=======\nthree\n{} theirs\n".format(MARK, ">" * 7))
        self.git("add", "a.txt")
        for command in ("precommit", "staged-markers"):
            with self.subTest(command=command):
                result = self.cli(command)
                self.assertNotEqual(0, result.returncode, command + " let staged conflict markers through")
                self.assertIn("a.txt", result.stdout)

    def test_a_clean_stage_passes_and_install_writes_a_pre_merge_commit_hook(self):
        self.write("a.txt", "one\n=======\nsetext underline is not a marker\n")
        self.git("add", "a.txt")
        self.assertEqual(0, self.cli("staged-markers").returncode)
        installed = self.cli("install")
        self.assertEqual(0, installed.returncode, installed.stdout + installed.stderr)
        hook = self.repo / ".git" / "hooks" / "pre-merge-commit"
        self.assertTrue(hook.exists(), "an automatic merge commit skips pre-commit; pre-merge-commit is its seam")
        self.assertIn("staged-markers", hook.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
