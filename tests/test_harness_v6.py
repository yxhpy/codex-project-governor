#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


class HarnessV6Test(unittest.TestCase):
    def run_json(self, args, check=True):
        proc = subprocess.run(args, text=True, capture_output=True, check=check, timeout=20)
        return json.loads(proc.stdout)

    def test_manifest_version(self):
        manifest = json.loads((ROOT / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['version'], '6.0.3')
        self.assertIn('Harness v6.0.3', manifest['description'])

    def test_orchestrator_uses_router_and_evidence(self):
        data = self.run_json([PY, str(ROOT / 'skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py'), '--request', 'Add dashboard export feature with tests'])
        self.assertEqual(data['runtime_version'], 'project-governor-harness-v6')
        self.assertIn('test-first-synthesizer', data['skill_sequence'])
        self.assertIn('evidence-manifest', data['skill_sequence'])
        self.assertIn('classification', data)
        self.assertIn('risk_score', data)

    def test_context_index_v2_redacts_secret(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / '.project-governor').mkdir()
            (project / 'AGENTS.md').write_text('Rules for auth token handling.\n', encoding='utf-8')
            (project / 'tasks/demo').mkdir(parents=True)
            (project / 'tasks/demo/ITERATION_PLAN.md').write_text('Auth login iteration history.\n', encoding='utf-8')
            (project / 'src').mkdir()
            (project / 'src/auth.py').write_text('API_TOKEN="sk-secretsecretsecretsecret"\ndef login():\n    return True\n', encoding='utf-8')
            built = self.run_json([PY, str(ROOT / 'skills/context-indexer/scripts/build_context_index.py'), '--project', str(project), '--write'])
            self.assertEqual(built['schema'], 'project-governor-context-index-v2')
            index = json.loads((project / '.project-governor/context/CONTEXT_INDEX.json').read_text(encoding='utf-8'))
            auth_entry = next(e for e in index['entries'] if e['path'] == 'src/auth.py')
            self.assertTrue(auth_entry['sensitive'])
            self.assertNotIn('sk-secretsecretsecretsecret', auth_entry['summary'])
            task_entry = next(e for e in index['entries'] if e['path'] == 'tasks/demo/ITERATION_PLAN.md')
            self.assertIn('task_history', task_entry['roles'])
            queried = self.run_json([PY, str(ROOT / 'skills/context-indexer/scripts/query_context_index.py'), '--project', str(project), '--request', 'auth login', '--route', 'risky_feature'])
            self.assertIn('confidence', queried)
            self.assertFalse(queried['read_all_initialization_docs'])

    def test_quality_gate_requires_evidence_when_strict(self):
        payload = {
            'level': 'strict',
            'route': 'risky_feature',
            'commands': ['python3 -m compileall tools skills tests'],
            'checks': {'compile': 'pass'},
            'require_evidence': True,
        }
        with tempfile.NamedTemporaryFile('w+', suffix='.json') as fh:
            json.dump(payload, fh)
            fh.flush()
            proc = subprocess.run([PY, str(ROOT / 'skills/quality-gate/scripts/run_quality_gate.py'), fh.name], text=True, capture_output=True)
        self.assertNotEqual(proc.returncode, 0)
        result = json.loads(proc.stdout)
        self.assertIn('evidence_manifest_missing', {f['type'] for f in result['findings']})

    def test_session_lifecycle_initializes_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            result = self.run_json([PY, str(ROOT / 'skills/session-lifecycle/scripts/session_lifecycle.py'), 'start', '--project', str(project), '--task-id', 'demo', '--route', 'standard_feature'])
            self.assertEqual(result['status'], 'started')
            self.assertTrue((project / '.project-governor/state/SESSION.json').exists())
            self.assertTrue((project / '.project-governor/state/FEATURES.json').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
