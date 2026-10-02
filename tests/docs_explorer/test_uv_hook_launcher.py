"""Exercise the installed Git hook launcher with uv but no Python on PATH."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which("git") and shutil.which("uv"), "Git and uv required for real launcher proof")
class UVHookLauncherTests(unittest.TestCase):
    def test_uv_only_launcher_preserves_hook_payload_arguments_and_exit(self):
        self.assert_uv_only_launcher()

    def test_uv_only_launcher_ignores_invalid_project_uv_configuration(self):
        self.assert_uv_only_launcher(invalid_config=True)

    def assert_uv_only_launcher(self, invalid_config=False):
        git = shutil.which("git")
        uv = shutil.which("uv")
        assert git is not None and uv is not None
        with tempfile.TemporaryDirectory(prefix="hook project ") as directory:
            root = Path(directory)
            if invalid_config:
                (root / "uv.toml").write_text("this is intentionally not valid TOML\n", encoding="utf-8", newline="\n")
            subprocess.run([git, "init", "-q", str(root)], check=True, capture_output=True)
            hooks = root / "docs/ai-forward-pack/hooks"
            hooks.mkdir(parents=True)
            shutil.copy2(ROOT / "pack/adapters/hooks/run-hook.sh", hooks / "run-hook.sh")
            (hooks / "probe.py").write_text(
                "import json,sys\n"
                "print(json.dumps({'payload': json.load(sys.stdin), 'args': sys.argv[1:]}))\n"
                "sys.exit(7)\n", encoding="utf-8", newline="\n",
            )
            env = dict(os.environ, UV_PYTHON=sys.executable, UV_NO_PROGRESS="1",
                       UV_OFFLINE="1", UV_PYTHON_DOWNLOADS="never",
                       UV_PYTHON_INSTALL_DIR=str(root / "uv-python"),
                       UV_CACHE_DIR=str(root / "uv-cache"))
            if os.name == "nt":
                git_root = Path(git).parent.parent
                directories = [str(Path(git).parent), str(git_root / "usr/bin"),
                               str(Path(uv).parent), str(Path(os.environ["SystemRoot"]) / "System32")]
            else:
                shim = root / "commands"
                shim.mkdir()
                shell = shutil.which("sh")
                assert shell is not None
                (shim / "sh").symlink_to(shell)
                (shim / "uv").symlink_to(uv)
                directories = [str(shim)]
            env["PATH"] = os.pathsep.join(directories)
            self.assertIsNone(shutil.which("python", path=env["PATH"]))
            self.assertIsNone(shutil.which("python3", path=env["PATH"]))
            payload = {"message": "A complete outcome — not a subset"}
            result = subprocess.run(
                [git, "-c", "alias.aif-hook=!sh", "aif-hook",
                 "docs/ai-forward-pack/hooks/run-hook.sh", "probe.py", "--example", "value with spaces"],
                cwd=root, env=env, input=json.dumps(payload), capture_output=True,
                text=True, encoding="utf-8", timeout=120,
            )
            self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout),
                             {"payload": payload, "args": ["--example", "value with spaces"]})


if __name__ == "__main__":
    unittest.main()
