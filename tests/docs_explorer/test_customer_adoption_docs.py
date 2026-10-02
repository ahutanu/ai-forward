"""Regression controls for copyable, reader-first adoption guidance."""
from pathlib import Path
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
PREVIEW = 'https://raw.githubusercontent.com/ahutanu/ai-forward/feat/one-command-adoption/bootstrap.py'

class CustomerAdoptionDocsTests(unittest.TestCase):
    def test_preview_quickstarts_lead_with_the_available_fork_entrypoint(self):
        for name in ('README.md','web/handbook/guides/get-started.md','pack/OVERVIEW.md'):
            with self.subTest(source=name):
                text=(ROOT/name).read_text(encoding='utf-8')
                commands=re.findall(r'^uv run --no-config --no-project --script ([^\n]+)$',text,re.M)
                self.assertTrue(commands,'The reader needs a copyable setup command')
                self.assertTrue(commands[0].startswith(PREVIEW+' --repo https://github.com/ahutanu/ai-forward.git --ref feat/one-command-adoption'),
                                'The first command must work in this preview, not depend on a future upstream release')

    def test_pack_readme_does_not_send_newcomers_to_a_nonexistent_manual_only_model(self):
        text=(ROOT/'pack/README.md').read_text(encoding='utf-8')
        self.assertNotIn('The pack ships no installer',text)
        self.assertIn('uv run --no-config --no-project --script',text)
        self.assertIn('Use the /deliver skill',text)

    def test_documented_progress_helper_ignores_broken_project_uv_configuration(self):
        text=(ROOT/'pack/commands/deliver/reference/checkpoints.md').read_text(encoding='utf-8')
        example=re.search(r'`(uv run [^`]+--help)`',text)
        self.assertIsNotNone(example,'The advanced helper example must be copyable')
        assert example is not None
        command=shlex.split(example.group(1))
        if not shutil.which('uv'):
            self.skipTest('uv is required to exercise the documented helper invocation')
        command[command.index('--python')+1]=sys.executable
        with tempfile.TemporaryDirectory(prefix='documented helper ') as folder:
            project=Path(folder)
            (project/'uv.toml').write_text('this is not valid = toml [\n',encoding='utf-8',newline='\n')
            installed=project/'docs/ai-forward-pack/scripts/delivery.py'
            installed.parent.mkdir(parents=True)
            installed.write_bytes((ROOT/'pack/scripts/delivery.py').read_bytes())
            result=subprocess.run(command,cwd=project,capture_output=True,text=True,encoding='utf-8',
                                  env={**os.environ,'UV_OFFLINE':'1','UV_PYTHON_DOWNLOADS':'never'},timeout=30)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn('resume',result.stdout)

    def test_quickstart_gives_finite_failure_pause_and_handback_examples(self):
        text=(ROOT/'web/handbook/guides/get-started.md').read_text(encoding='utf-8')
        for phrase in ('If setup fails', 'Command not found', 'Source unavailable',
                       'Authentication failed', 'Project checks unavailable',
                       'Approve', 'Change', 'Decline', 'Stop this task',
                       'Completed', 'Remaining', 'Best next action'):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)
        self.assertRegex(text, r'Task id: `[^`]+`')
        self.assertIn('A blocked check is not a passed check', text)
        self.assertIn('If the checkpoint is missing or damaged', text)
        self.assertIn('enclosing Git root', text)
        self.assertIn('inspect the project diff', text)

if __name__=='__main__':
    unittest.main()
