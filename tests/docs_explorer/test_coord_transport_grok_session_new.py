"""XPORT-A: Grok's watcher acknowledgement can arrive BEFORE the session/new response.

Measured 2026-10-03 in x-harness-x-model-bench (runs w2-g1-e1e4 and w2-enva-e1e4, Grok 1.0.41,
Windows): 2 of 3 dispatches failed `protocol_error` at phase `session/new`, because Grok sent
`{"id": "skills-reload", "jsonrpc": "2.0", "result": {"result": {"reloaded": 0}}}` before the
session/new response. The transport accepted that frame only inside session/prompt, and only with
`reloaded: 1`. A protocol client that tolerates an interleaved message only in the phase where it
was first seen is the class.

These tests drive `_Session.acp` with an in-memory wire, so they run on every platform (the
subprocess suite in test_coord_transport.py is POSIX-only). The compatibility stays narrow: the
named watcher ids, the exact shape, and the 1.0.34 release floor.
"""
import importlib.util
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "pack" / "scripts" / "coord_transport.py"
spec = importlib.util.spec_from_file_location("coord_transport_session_new", SCRIPT)
ct = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ct)

WATCHER = {"id": "skills-reload", "jsonrpc": "2.0", "result": {"result": {"reloaded": 0}}}


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


def _run(version, middle):
    init = {"jsonrpc": "2.0", "id": 1, "result": {
        "protocolVersion": 1, "agentInfo": {"name": "grok", "version": version},
        "_meta": {"grokShell": True, "agentVersion": version}}}
    created = {"jsonrpc": "2.0", "id": 2, "result": {"sessionId": "s-1"}}
    result = {"session_id": None, "compatibility_responses": 0, "reported_version": None,
              "reported_version_source": None, "progress_updates": 0}
    session = ct._Session(_Wire([init, *middle, created]), result, lambda event: None,
                          lambda left: True, [])
    try:
        session.acp("/tmp", [], [], None, False, None, None)
    except ct._Failure as failure:
        return result, failure, session
    return result, None, session


class GrokSessionNewWatcherTests(unittest.TestCase):
    def test_watcher_ack_before_session_new_response_creates_the_session(self):
        for reloaded in (0, 1):
            with self.subTest(reloaded=reloaded):
                ack = {"id": "skills-reload", "jsonrpc": "2.0", "result": {"result": {"reloaded": reloaded}}}
                result, failure, session = _run("1.0.41", [ack])
                self.assertIsNone(failure, "the measured order must create the session")
                self.assertEqual("session/new", session.phase)
                self.assertEqual(("s-1", 1), (result["session_id"], result["compatibility_responses"]))

    def test_anything_else_unsolicited_during_session_new_is_still_a_protocol_error(self):
        cases = [
            ("1.0.41", {"id": "surprise", "jsonrpc": "2.0", "result": {"result": {"reloaded": 0}}}),
            ("1.0.41", {"id": "skills-reload", "jsonrpc": "2.0", "result": {"result": {"reloaded": 0, "x": 1}}}),
            ("1.0.41", {"id": "skills-reload", "jsonrpc": "2.0", "result": {"result": {"reloaded": 2}}}),
            ("1.0.33", WATCHER),
        ]
        for version, message in cases:
            with self.subTest(version=version, message=message):
                result, failure, session = _run(version, [message])
                self.assertIsNotNone(failure)
                self.assertEqual(("protocol_error", "session/new"), (failure.code, session.phase))
                self.assertIsNone(result["session_id"])


def _run_initialize(version, ack, grok_shell=True):
    """XPORT-A, initialize: measured 2026-10-05 (run w2-k2a-e1e4, Grok 1.0.41,
    `protocol_error_phase: "initialize"`), the ack arrived before the initialize response.
    The release is only known once that response arrives, so the floor is checked then."""
    meta = {"grokShell": True, "agentVersion": version} if grok_shell else {}
    init = {"jsonrpc": "2.0", "id": 1, "result": {
        "protocolVersion": 1, "agentInfo": {"name": "grok", "version": version}, "_meta": meta}}
    created = {"jsonrpc": "2.0", "id": 2, "result": {"sessionId": "s-1"}}
    result = {"session_id": None, "compatibility_responses": 0, "reported_version": None,
              "reported_version_source": None, "progress_updates": 0}
    session = ct._Session(_Wire([ack, init, created]), result, lambda event: None,
                          lambda left: True, [])
    try:
        session.acp("/tmp", [], [], None, False, None, None)
    except ct._Failure as failure:
        return result, failure, session
    return result, None, session


class GrokInitializeWatcherTests(unittest.TestCase):
    def test_watcher_ack_before_the_initialize_response_creates_the_session(self):
        for ident in ("skills-reload", "workflows-reload"):
            for reloaded in (0, 1):
                with self.subTest(ident=ident, reloaded=reloaded):
                    ack = {"id": ident, "jsonrpc": "2.0", "result": {"result": {"reloaded": reloaded}}}
                    result, failure, session = _run_initialize("1.0.41", ack)
                    self.assertIsNone(failure, "the measured order must initialize and create the session")
                    self.assertEqual(("s-1", 1), (result["session_id"], result["compatibility_responses"]))

    def test_anything_else_unsolicited_during_initialize_is_still_a_protocol_error(self):
        cases = [
            ("1.0.41", {"id": "surprise", "jsonrpc": "2.0", "result": {"result": {"reloaded": 0}}}, True),
            ("1.0.41", {"id": "skills-reload", "jsonrpc": "2.0", "result": {"result": {"reloaded": 0, "x": 1}}}, True),
            ("1.0.41", {"id": "skills-reload", "jsonrpc": "2.0", "result": {"result": {"reloaded": 2}}}, True),
            ("1.0.41", {"id": "skills-reload", "jsonrpc": "2.0", "result": {"result": {"reloaded": True}}}, True),
            ("1.0.33", WATCHER, True),
            ("1.0.41", WATCHER, False),
        ]
        for version, message, grok_shell in cases:
            with self.subTest(version=version, message=message, grok_shell=grok_shell):
                result, failure, session = _run_initialize(version, message, grok_shell)
                self.assertIsNotNone(failure)
                self.assertEqual(("protocol_error", "initialize"), (failure.code, session.phase))
                self.assertIsNone(result["session_id"])


if __name__ == "__main__":
    unittest.main()
