"""Narrow upstream integration controls for authored adoption metadata.

Any disposable Git history built here is a synthetic regression fixture, not
published-source installation proof. Tests require no historical SHA or network.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class UpstreamAdoptionDocsTests(unittest.TestCase):
    def test_manual_guidance_leaves_explorer_instantiation_to_content_skills(self):
        cases = (
            ('pack/README.md', '**Install with the one-line setup above',
             'the Docs Explorer at `docs/index.html`'),
            ('pack/OVERVIEW.md', 'For expert installation or project-specific reconciliation',
             'the Docs Explorer template → `docs/index.html` (one-time copy)'),
        )
        for name, start, obsolete in cases:
            with self.subTest(source=name):
                text = (ROOT / name).read_text(encoding='utf-8')
                paragraph = text.split(start, 1)[1].split('\n\n', 1)[0]
                self.assertNotIn(obsolete, paragraph)
                self.assertIn('the Docs Explorer template', paragraph)
                self.assertIn('first content-creating skill', paragraph)
                self.assertIn('instantiate at `docs/index.html`', paragraph)
                self.assertIn('not copied by install', paragraph)


class UpstreamRefreshMetadataTests(unittest.TestCase):
    def test_current_delta_advances_revision_and_names_complete_refresh(self):
        text = (ROOT / 'pack/adapters/INSTALL.md').read_text(encoding='utf-8')
        frontmatter = text.split('---\n', 2)[1]
        self.assertRegex(frontmatter, r"(?m)^revision: 103$")
        self.assertIn("bundle_version: '2026.10.05.1'", frontmatter)
        for source in ('adapters/hooks/session-start.py', 'scripts/pack-apply.py',
                       'scripts/delivery.py', 'commands/deliver/reference/checkpoints.md',
                       'adapters/hooks/git-identity-guard.py',
                       'adapters/hooks/claude-code.settings.hooks.json',
                       'adapters/hooks/copilot.ai-forward-hooks.json',
                       'adapters/hooks/grok.ai-forward-hooks.json',
                       'adapters/hooks/README.md', 'commands/addpacktorepo/SKILL.md',
                       'adapters/copilot/prompts/addpacktorepo.prompt.md',
                       'README.md', 'OVERVIEW.md', 'context-budget.json'):
            with self.subTest(changed_source=source):
                self.assertIn("'" + source + "'", frontmatter)
        for boundary in ('docs/audit/.run-starts.json', 'docs/audit/.run-starts.json.tmp',
                         '.agents/log/audit/.run-starts.json',
                         '.agents/log/audit/.run-starts.json.tmp'):
            self.assertIn(boundary, frontmatter)
        for instruction in ('SOURCE', 'plan --target', 'apply --target',
                            'full deployment map', 'complete deliver skill directories',
                            'including both references', 'not --force', 'durable audit and coordination logs',
                            'Antigravity', 'not wired', 'Codex', 'opt-in',
                            'authenticated consent', 'model compliance'):
            self.assertIn(instruction, frontmatter)
        self.assertNotIn('area: delivery-checkpoint-boundaries', frontmatter,
                         'Only the current delta belongs in active frontmatter')

    def test_previous_delta_and_entire_archive_remain_exact_bytes(self):
        raw = (ROOT / 'pack/adapters/INSTALL.md').read_bytes()
        blocks = re.findall(rb'<details>\n<summary>.*?\n</details>', raw, re.S)
        self.assertEqual(4, len(blocks))
        self.assertIn('Revision 102 — 3 October 2026'.encode('utf-8'), blocks[0])
        row = blocks[0].split(b'```yaml\nchanges:\n', 1)[1].split(b'\n```', 1)[0]
        self.assertEqual('37c677dc788ac371b1bf4716522f9d23367068ac0e914678b46fc2a2deeabfea',
                         hashlib.sha256(row).hexdigest(), 'Move the exact previous changes row')
        # Complete raw collapsed blocks, including all long original history rows.
        # Hashes avoid requiring an old Git object in a shallow checkout.
        expected = (
            (1038, '9a56bc7f409c6c5e5f01cbe0917840cac3d3722a95ecc34465d6d3194443334f'),
            (753, 'c6b40766a5fc4f6ea47f001ed4e292dddce725204c5b00962f0910a0ff9eb674'),
            (187189, '1dc4d0d7b3cc4df881a208f02c8ce3ac02a907488f1a1b5c3df390eee4c462f7'),
        )
        self.assertEqual(expected, tuple((len(b), hashlib.sha256(b).hexdigest()) for b in blocks[1:]))


class Existing102RefreshTests(unittest.TestCase):
    def test_existing_102_refreshes_changed_bytes_and_preserves_project_settings(self):
        if not shutil.which('git'):
            self.skipTest('Git is an installer prerequisite')
        # This two-commit source history is SYNTHETIC: it models revision-based
        # refresh decisions, not the exact bytes/behavior of a published old pack.
        # Build it locally so shallow CI needs no old source SHA or network fetch.
        with tempfile.TemporaryDirectory(prefix='synthetic pack refresh ') as folder:
            source = Path(folder) / 'source'
            target = Path(folder) / 'target'
            shutil.copytree(ROOT / 'pack', source / 'pack', ignore=shutil.ignore_patterns('__pycache__'))
            target.mkdir()
            env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
            env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
                       GIT_TERMINAL_PROMPT='0', PYTHONDONTWRITEBYTECODE='1')

            def run(command, cwd):
                result = subprocess.run(command, cwd=cwd, env=env, capture_output=True,
                                        text=True, encoding='utf-8', timeout=90)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                return result.stdout

            def git(*args):
                return run(['git', '-c', 'core.autocrlf=false', '-c', 'user.name=Regression Fixture',
                            '-c', 'user.email=fixture@example.invalid', *args], source)

            def apply(mode, *args):
                return json.loads(run([sys.executable, str(source / 'pack/scripts/pack-apply.py'),
                                       mode, '--target', str(target), '--no-baselines', '--json',
                                       *args], target))

            def snapshot():
                return {p.relative_to(target).as_posix(): p.read_bytes()
                        for p in target.rglob('*') if p.is_file()}

            # Latest authored bytes are copied first; modify only the disposable
            # baseline into deliberately distinguishable old fixture content.
            changed_text = (
                'adapters/hooks/session-start.py', 'scripts/delivery.py', 'scripts/pack-apply.py',
                'adapters/hooks/git-identity-guard.py',
                'adapters/hooks/README.md', 'commands/addpacktorepo/SKILL.md',
                'adapters/copilot/prompts/addpacktorepo.prompt.md', 'README.md', 'OVERVIEW.md',
            )
            configs = ('claude-code.settings.hooks.json', 'copilot.ai-forward-hooks.json',
                       'grok.ai-forward-hooks.json')
            changed = [*changed_text, 'context-budget.json', 'adapters/INSTALL.md',
                       *('adapters/hooks/' + name for name in configs)]
            latest = {name: (source / 'pack' / name).read_bytes() for name in changed}
            for name in changed_text:
                with (source / 'pack' / name).open('ab') as stream:
                    stream.write(b'\n# Synthetic revision102 baseline, not published source.\n')
            install = source / 'pack/adapters/INSTALL.md'
            install.write_bytes(re.sub(rb'(?m)^revision: \d+$', b'revision: 102', latest['adapters/INSTALL.md']))
            budget = source / 'pack/context-budget.json'
            old_budget = json.loads(budget.read_text(encoding='utf-8'))
            old_budget['synthetic_revision102_fixture'] = True
            budget.write_text(json.dumps(old_budget, indent=2) + '\n', encoding='utf-8', newline='\n')
            for name in configs:
                config = source / 'pack/adapters/hooks' / name
                old = json.loads(config.read_text(encoding='utf-8'))
                for event, entries in old['hooks'].items():
                    old['hooks'][event] = [entry for entry in entries
                                           if 'git-identity-guard.py' not in json.dumps(entry)]
                config.write_text(json.dumps(old, indent=2) + '\n', encoding='utf-8', newline='\n')
            git('init')
            git('add', 'pack')
            git('commit', '-m', 'Synthetic revision102 baseline fixture')

            product = target / 'product.txt'
            product.write_bytes(b'Project-owned content must survive.\n')
            index = target / 'docs/docs-index.js'
            index.parent.mkdir(parents=True)
            index.write_bytes(b'window.DOCS_INDEX = {projectOwned: true};\n')
            settings = target / '.claude/settings.json'
            settings.parent.mkdir()
            local_hook = {'matcher': 'ProjectOnly', 'hooks': [
                {'type': 'command', 'command': 'project-local-check', 'timeout': 17}]}
            custom = {'permissions': {'allow': ['Bash(git status)']},
                      'env': {'PROJECT_SETTING': 'preserved'},
                      'hooks': {'PreToolUse': [local_hook]}}
            settings.write_text(json.dumps(custom) + '\n', encoding='utf-8', newline='\n')
            agy = target / '.agents/hooks.json'
            agy.parent.mkdir()
            local_bundle = {'enabled': True, 'Stop': [{'command': 'project-local-stop'}]}
            agy.write_text(json.dumps({'project-local': local_bundle}) + '\n', encoding='utf-8', newline='\n')
            apply('apply', '--install')
            self.assertIn(b'revision: 102\n', (target / 'docs/ai-forward-pack/INSTALL.md').read_bytes())
            before = snapshot()
            for name, data in latest.items():
                (source / 'pack' / name).write_bytes(data)
            git('add', 'pack')
            git('commit', '-m', 'Synthetic latest integration fixture')
            plan = apply('plan')
            self.assertEqual(before, snapshot(), 'Full-map plan must not write the existing target')
            apply('apply')

            # Byte equality catches same-revision KEEP even when apply exits zero.
            # Script/hook/config refresh is exercised through the actual source CLI.
            destinations = {
                'adapters/hooks/session-start.py': 'docs/ai-forward-pack/hooks/session-start.py',
                'scripts/delivery.py': 'docs/ai-forward-pack/scripts/delivery.py',
                'scripts/pack-apply.py': 'docs/ai-forward-pack/scripts/pack-apply.py',
                'adapters/hooks/git-identity-guard.py': 'docs/ai-forward-pack/hooks/git-identity-guard.py',
                'adapters/hooks/README.md': 'docs/ai-forward-pack/hooks/README.md',
                'adapters/hooks/copilot.ai-forward-hooks.json': '.github/hooks/ai-forward.json',
                'adapters/hooks/grok.ai-forward-hooks.json': '.grok/hooks/ai-forward.json',
                'context-budget.json': 'docs/ai-forward-pack/context-budget.json',
                'README.md': 'docs/ai-forward-pack/README.md',
                'OVERVIEW.md': 'docs/ai-forward-pack/OVERVIEW.md',
            }
            for name, destination in destinations.items():
                self.assertEqual(latest[name], (target / destination).read_bytes(), destination)
            for host in ('.claude', '.grok', '.agents'):
                self.assertEqual(latest['commands/addpacktorepo/SKILL.md'],
                                 (target / host / 'skills/addpacktorepo/SKILL.md').read_bytes())
            self.assertEqual(latest['adapters/copilot/prompts/addpacktorepo.prompt.md'],
                             (target / '.github/prompts/addpacktorepo.prompt.md').read_bytes())
            self.assertEqual(latest['adapters/INSTALL.md'], (target / 'docs/ai-forward-pack/INSTALL.md').read_bytes())
            self.assertEqual(103, plan['source_revision'])
            self.assertEqual(102, plan['target_revision'])
            self.assertEqual('UPDATE', next(row['action'] for row in plan['rows']
                                           if row['path'] == 'docs/ai-forward-pack/hooks/session-start.py'))
            self.assertEqual(before['product.txt'], product.read_bytes())
            self.assertEqual(before['docs/docs-index.js'], index.read_bytes())
            merged = json.loads(settings.read_text(encoding='utf-8'))
            for key in ('permissions', 'env'):
                self.assertEqual(custom[key], merged[key])
            expected = json.loads(latest['adapters/hooks/claude-code.settings.hooks.json'])
            for event, entries in expected['hooks'].items():
                self.assertCountEqual(entries + ([local_hook] if event == 'PreToolUse' else []),
                                      merged['hooks'][event])
            self.assertEqual(local_bundle, json.loads(agy.read_text(encoding='utf-8'))['project-local'])
            self.assertFalse((target / 'docs/index.html').exists(), 'Refresh is not Explorer opt-in')
            refreshed = snapshot()
            apply('apply')
            self.assertEqual(refreshed, snapshot(), 'Repeating a refresh preserves installed and project bytes')


class UpstreamWorkflowPolicyTests(unittest.TestCase):
    def test_adoption_workflow_is_manual_only_and_routes_session_resume_regression(self):
        raw = (ROOT / '.github/workflows/adoption-entrypoints.yml').read_bytes()
        triggers = raw.split(b'\non:\n', 1)[1].split(b'permissions:\n', 1)[0]
        self.assertEqual(b'  workflow_dispatch:\n', triggers,
                         'Follow the upstream manual-only Actions policy')
        routing = next(line for line in raw.splitlines()
                       if b'run: python -m pytest ' in line)
        added_tests = (
            b' tests/docs_explorer/test_delivery_session_start.py'
            b' tests/docs_explorer/test_upstream_adoption_integration.py'
            b' tests/docs_explorer/test_git_identity_guard.py'
            b' tests/docs_explorer/test_session_start_hook.py'
            b' tests/docs_explorer/test_pack_apply.py'
        )
        for name in added_tests.split():
            self.assertIn(name, routing)
        # Undo the only authorized job edit and compare the complete native proof
        # body, not just headings. Permissions, every OS and native cmd remain.
        jobs = raw[raw.index(b'permissions:\n'):]
        self.assertEqual(1, jobs.count(added_tests))
        unchanged_jobs = jobs.replace(added_tests, b'', 1)
        self.assertEqual('43c5bf864846a145f963e1d05282a6cddbed778571a93dbb89e47be782f9794d',
                         hashlib.sha256(unchanged_jobs).hexdigest())
        self.assertIn(b'os: [ubuntu-latest, macos-latest, windows-latest]', jobs)
        self.assertIn(b'shell: cmd', jobs)


if __name__ == '__main__':
    unittest.main()
