import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "pack" / "scripts" / "render-markdown.py"


def load_module():
    spec = importlib.util.spec_from_file_location("render_markdown", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RenderMarkdownTests(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def test_RenderMarkdown_CommonStructure_ProducesSemanticHtml(self):
        markdown = """---
title: Hidden metadata
---
# Proposal

| Question | Recommendation |
|---|---|
| Scope? | Keep it small |

- One
- Two

`code` and **strong**.
"""
        rendered = self.module.render_markdown(markdown)
        self.assertIn("<h1>Proposal</h1>", rendered)
        self.assertIn("<table>", rendered)
        self.assertIn("<ul><li>One</li><li>Two</li></ul>", rendered)
        self.assertNotIn("Hidden metadata", rendered)

    def test_RenderMarkdown_RawHtmlAndUnsafeLink_EscapesContent(self):
        rendered = self.module.render_markdown(
            "# Safe\n\n<script>alert(1)</script>\n\n[click](javascript:alert(1))"
        )
        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertNotIn('href="javascript:', rendered)

    def test_Cli_DefaultOutput_WritesSiblingHtml(self):
        source = self.root / "proposal.md"
        source.write_text("# Proposal\n", encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), str(source)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        target = source.with_suffix(".html")
        self.assertTrue(target.exists())
        self.assertIn("<h1>Proposal</h1>", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
