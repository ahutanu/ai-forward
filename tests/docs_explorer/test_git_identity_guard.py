"""PK-07's mechanical control: AL0.2 says in prose that neither a pack script nor the agent
running it may invent a git identity to force a blocked commit through. This is the second
half -- a PreToolUse hook that refuses the shell command itself, so the rule holds even when
the agent forgets it. The decision function is pure so the oracle is exact; the subprocess
tests pin the host contracts (exit 2 denies preToolUse on Claude Code, Grok Build's
Claude-format hooks, and Copilot CLI -- reread-guard.py's own documented contract)."""
import importlib.util
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GUARD = ROOT / "pack" / "adapters" / "hooks" / "git-identity-guard.py"


def _load():
    spec = importlib.util.spec_from_file_location("git_identity_guard", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class EvaluateTests(unittest.TestCase):
    def setUp(self):
        self.g = _load()

    def test_git_config_user_name_with_a_value_is_blocked(self):
        reason = self.g.evaluate("claude", {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                            "tool_input": {"command": 'git config user.name "CI Bot"'}})
        self.assertIsNotNone(reason)
        self.assertIn("PK-07", reason)

    def test_git_config_global_user_email_with_a_value_is_blocked(self):
        reason = self.g.evaluate("claude", {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                            "tool_input": {"command": "git config --global user.email a@b.com"}})
        self.assertIsNotNone(reason)

    def test_inline_dash_c_override_is_blocked(self):
        reason = self.g.evaluate("claude", {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                            "tool_input": {"command": 'git -c user.name=bot -c user.email=a@b commit -m x'}})
        self.assertIsNotNone(reason)

    def test_chained_with_other_commands_is_still_caught(self):
        reason = self.g.evaluate("claude", {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                            "tool_input": {"command": 'git add -A && git config user.name "x" && git commit -m y'}})
        self.assertIsNotNone(reason)

    def test_reading_the_identity_is_never_blocked(self):
        reason = self.g.evaluate("claude", {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                            "tool_input": {"command": "git config user.name"}})
        self.assertIsNone(reason)

    def test_get_flag_is_never_blocked(self):
        reason = self.g.evaluate("claude", {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                            "tool_input": {"command": "git config --get user.email"}})
        self.assertIsNone(reason)

    def test_an_unrelated_command_is_never_blocked(self):
        reason = self.g.evaluate("claude", {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                            "tool_input": {"command": "git commit -m 'normal change'"}})
        self.assertIsNone(reason)

    def test_non_pretooluse_events_are_ignored(self):
        reason = self.g.evaluate("claude", {"hook_event_name": "UserPromptSubmit",
                                            "tool_input": {"command": 'git config user.name "x"'}})
        self.assertIsNone(reason)

    def test_grok_camelcase_payload_is_caught(self):
        reason = self.g.evaluate("grok", {"hookEventName": "PreToolUse", "toolName": "Bash",
                                          "toolInput": {"command": 'git config user.email "x@y"'}})
        self.assertIsNotNone(reason)

    def test_copilot_payload_is_caught(self):
        reason = self.g.evaluate("copilot", {"sessionId": "s", "toolName": "bash",
                                             "toolArgs": {"command": 'git config user.name "x"'}})
        self.assertIsNotNone(reason)

    def test_no_command_like_field_is_never_blocked(self):
        reason = self.g.evaluate("claude", {"hook_event_name": "PreToolUse", "tool_name": "Read",
                                            "tool_input": {"file_path": "/x/y.md"}})
        self.assertIsNone(reason)


class MainSubprocessTests(unittest.TestCase):
    def _run(self, host, payload):
        return subprocess.run([sys.executable, str(GUARD), "--host", host], input=json.dumps(payload),
                              capture_output=True, text=True, timeout=30)

    def test_claude_blocks_with_exit_2_and_a_stderr_reason(self):
        r = self._run("claude", {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                 "tool_input": {"command": 'git config user.name "x"'}})
        self.assertEqual(2, r.returncode)
        self.assertIn("PK-07", r.stderr)
        self.assertEqual("", r.stdout.strip(), "never prints to stdout (that reaches the model as context)")

    def test_claude_allows_a_normal_commit(self):
        r = self._run("claude", {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                                 "tool_input": {"command": "git commit -m 'normal change'"}})
        self.assertEqual(0, r.returncode)

    def test_grok_blocks_with_exit_2(self):
        r = self._run("grok", {"hookEventName": "PreToolUse", "toolName": "Bash",
                               "toolInput": {"command": 'git config --global user.email "x@y"'}})
        self.assertEqual(2, r.returncode)
        self.assertIn("PK-07", r.stderr)

    def test_copilot_blocks_with_exit_2(self):
        r = self._run("copilot", {"sessionId": "s", "toolName": "bash",
                                  "toolArgs": {"command": 'git config user.name "x"'}})
        self.assertEqual(2, r.returncode)
        self.assertIn("PK-07", r.stderr)

    def test_malformed_stdin_is_fail_open(self):
        r = subprocess.run([sys.executable, str(GUARD), "--host", "claude"], input="not json",
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(0, r.returncode, "a guard that cannot evaluate must never block a real tool call")

    def test_agy_is_not_a_supported_host(self):
        """Antigravity's PreToolUse deny contract is unverified in this pack (only `allow` is
        observed, by reread-guard.py); rather than guess a shape that might silently fail
        open or block everything, this guard is not wired for agy (left prose-only, AL0.2)."""
        r = self._run("agy", {})
        self.assertNotEqual(0, r.returncode, "agy is deliberately not an accepted --host value")


class HookConfigsWireTheGuardWhereGrounded(unittest.TestCase):
    """The guard is wired into every host config whose PreToolUse deny contract this pack
    has grounded (claude, grok, copilot) and deliberately absent from agy's (unverified)."""

    def test_claude_settings_snippet_wires_pretooluse(self):
        snippet = json.loads((ROOT / "pack" / "adapters" / "hooks" / "claude-code.settings.hooks.json")
                             .read_text(encoding="utf-8"))
        cmds = [h["command"] for entry in snippet["hooks"].get("PreToolUse", []) for h in entry.get("hooks", [])]
        self.assertTrue(any("git-identity-guard.py" in c for c in cmds), "PreToolUse must run the guard")

    def test_grok_config_wires_pretooluse(self):
        config = json.loads((ROOT / "pack" / "adapters" / "hooks" / "grok.ai-forward-hooks.json")
                            .read_text(encoding="utf-8"))
        cmds = [h["command"] for entry in config["hooks"].get("PreToolUse", []) for h in entry.get("hooks", [])]
        self.assertTrue(any("git-identity-guard.py" in c for c in cmds), "PreToolUse must run the guard")

    def test_copilot_config_wires_pretooluse(self):
        config = json.loads((ROOT / "pack" / "adapters" / "hooks" / "copilot.ai-forward-hooks.json")
                            .read_text(encoding="utf-8"))
        cmds = [h.get("bash", "") for h in config["hooks"].get("preToolUse", [])]
        self.assertTrue(any("git-identity-guard.py" in c for c in cmds), "preToolUse must run the guard")

    def test_agy_config_does_not_claim_the_guard(self):
        config = json.loads((ROOT / "pack" / "adapters" / "hooks" / "agy.ai-forward-hooks.json")
                            .read_text(encoding="utf-8"))
        self.assertNotIn("git-identity-guard", json.dumps(config),
                         "agy's PreToolUse deny contract is unverified; do not claim enforcement")


if __name__ == "__main__":
    unittest.main()
