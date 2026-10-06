"""SERVE-A root cause: a Grok worker's model pin was never applied over ACP.

Measured 2026-10-05 in x-harness-x-model-bench (run w2-g3-e1e4, Grok 1.0.41, Windows): argv carried
`-m grok-4.7`, but the runner passed `expected_model` only for Copilot, so the transport never called
`session/set_model`. Grok's ACP default (`currentModelId` grok-4.6) answered: `selected_model`
grok-4.6, `selected_model_set` false, first response from grok-4.6-build.

Two halves. The runner derives the pin from argv for Grok as it does for Copilot. The transport, once
`session/set_model` answers, reads the model the session reports and fails closed when it is not the
pin. Grok 1.0.41 reports it as `result._meta.model` = `{"Ok": "<model id>"}` (spike, 2026-10-05:
`grok agent --no-leader -m grok-4.7 stdio`, initialize -> authenticate -> session/new -> set_model,
no prompt). A response with no report (Copilot answers `{}`) keeps the earlier behaviour; Copilot's
served model is checked afterwards from its native events.

The transport half drives `_Session.acp` with an in-memory wire, so it runs on every platform.
"""
import importlib.util
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

SOURCE = Path(__file__).resolve().parents[2] / "pack" / "scripts"
spec = importlib.util.spec_from_file_location("coord_transport_grok_pin", SOURCE / "coord_transport.py")
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)

# The argv of the consuming repo's Grok workers (docs/coordination/eval-q0/q0-contract.json).
GROK_ARGV = ["grok", "agent", "--no-leader", "-m", "grok-4.7", "--reasoning-effort", "high", "stdio"]


class _Wire:
    def __init__(self, script):
        self.script, self.sent = list(script), []
        self.deadline = time.monotonic() + 60
        self.last_frame_bytes = 0

    def queue(self, message):
        self.sent.append(message)

    def receive(self):
        return self.script.pop(0)

    def check(self):
        pass


def _run(set_model_result, expected="grok-4.7"):
    init = {"jsonrpc": "2.0", "id": 1, "result": {
        "protocolVersion": 1, "agentInfo": {"name": "grok", "version": "1.0.41"},
        "_meta": {"grokShell": True, "agentVersion": "1.0.41"}}}
    created = {"jsonrpc": "2.0", "id": 2, "result": {"sessionId": "s-1", "models": {"currentModelId": "grok-4.6"}}}
    selected = {"jsonrpc": "2.0", "id": 3, "result": set_model_result}
    result = {"session_id": None, "compatibility_responses": 0, "reported_version": None,
              "reported_version_source": None, "progress_updates": 0, "selected_model": None,
              "selected_model_set": False}
    wire = _Wire([init, created, selected])
    session = ct._Session(wire, result, lambda event: None, lambda left: True, [])
    try:
        session.acp("/tmp", [], [], None, False, None, expected)
    except ct._Failure as failure:
        return result, failure, wire
    return result, None, wire


class GrokModelPinTransportTests(unittest.TestCase):
    def test_a_confirmed_pin_becomes_the_selected_model(self):
        result, failure, wire = _run({"_meta": {"model": {"Ok": "grok-4.7"}}})
        self.assertIsNone(failure)
        self.assertEqual({"sessionId": "s-1", "modelId": "grok-4.7"}, wire.sent[2]["params"])
        self.assertEqual(("grok-4.7", True), (result["selected_model"], result["selected_model_set"]),
                         "the session confirmed the pin, yet the record still names the ACP default")

    def test_a_reported_model_other_than_the_pin_fails_closed(self):
        for reported in ({"model": {"Ok": "grok-4.6"}}, {"model": {"Err": "unknown model"}},
                         {"model": "grok-4.7"}, {"model": {"Ok": "grok-4.7", "Err": "x"}}):
            with self.subTest(reported=reported):
                result, failure, wire = _run({"_meta": reported})
                self.assertIsNotNone(failure, "the session reported another model and the attempt went on")
                self.assertEqual(("session_model_mismatch", "blocked"), (failure.code, failure.outcome))

    def test_a_response_without_a_model_report_keeps_the_earlier_behaviour(self):
        for response in ({}, {"_meta": {}}):
            with self.subTest(response=response):
                result, failure, wire = _run(response)
                self.assertIsNone(failure)
                self.assertEqual(("grok-4.6", True), (result["selected_model"], result["selected_model_set"]))


class GrokModelPinRunnerTests(unittest.TestCase):
    def setUp(self):
        with mock.patch.object(sys, "path", [str(SOURCE), *sys.path]):
            runner_spec = importlib.util.spec_from_file_location("runner_grok_pin", SOURCE / "coord-runner.py")
            self.runner = importlib.util.module_from_spec(runner_spec)
            runner_spec.loader.exec_module(self.runner)

    def test_the_grok_argv_pin_is_the_expected_model(self):
        self.assertTrue(hasattr(self.runner, "expected_model"),
                        "the runner derives an expected model for Copilot only; a Grok pin is never applied")
        self.assertEqual("grok-4.7", self.runner.expected_model({"harness": "grok", "argv": GROK_ARGV}))
        for argv in (["grok", "agent", "--model", "grok-4.7", "stdio"], ["grok", "agent", "--model=grok-4.7", "stdio"]):
            with self.subTest(argv=argv):
                self.assertEqual("grok-4.7", self.runner.expected_model({"harness": "grok", "argv": argv}))

    def test_an_unpinned_grok_or_another_harness_has_no_expected_model(self):
        self.assertTrue(hasattr(self.runner, "expected_model"))
        self.assertIsNone(self.runner.expected_model({"harness": "grok", "argv": ["grok", "agent", "stdio"]}))
        self.assertIsNone(self.runner.expected_model({"harness": "codex", "argv": ["codex-acp", "-m", "x"]}))

    def test_an_ambiguous_grok_pin_is_refused(self):
        self.assertTrue(hasattr(self.runner, "expected_model"))
        for argv in (["grok", "agent", "-m", "a", "-m", "b", "stdio"], ["grok", "agent", "-m"],
                     ["grok", "agent", "-m", "--yolo", "stdio"], ["grok", "agent", "--model=", "stdio"]):
            with self.subTest(argv=argv):
                with self.assertRaises(self.runner.Refused) as raised:
                    self.runner.expected_model({"harness": "grok", "argv": argv})
                self.assertEqual("RUN-GROK-MODEL", raised.exception.code)


if __name__ == "__main__":
    unittest.main()
