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
HARNESS_DOCTOR = ROOT / 'skills/harness-doctor/scripts/doctor.py'


class HarnessV6Test(unittest.TestCase):
    def run_json(self, args, check=True):
        proc = subprocess.run(args, text=True, capture_output=True, check=check, timeout=20)
        return json.loads(proc.stdout)

    def test_manifest_version(self):
        manifest = json.loads((ROOT / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['version'], '6.2.5')
        self.assertIn('Harness v6.2.5', manifest['description'])

    def test_harness_doctor_uses_feature_matrix_current_latest(self):
        data = self.run_json([PY, str(HARNESS_DOCTOR), '--project', str(ROOT), '--execution-readiness'])
        self.assertEqual(data['status'], 'pass')
        self.assertFalse(
            any('manifest version' in warning for warning in data['warnings']),
            data['warnings'],
        )

    def test_orchestrator_uses_router_and_evidence(self):
        data = self.run_json([PY, str(ROOT / 'skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py'), '--request', 'Add dashboard export feature with tests'])
        self.assertEqual(data['runtime_version'], 'project-governor-harness-v6')
        self.assertIn('test-first-synthesizer', data['skill_sequence'])
        self.assertIn('engineering-standards-governor', data['skill_sequence'])
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
            self.assertIn('docs_manifest', built)
            index = json.loads((project / '.project-governor/context/CONTEXT_INDEX.json').read_text(encoding='utf-8'))
            manifest = json.loads((project / '.project-governor/context/DOCS_MANIFEST.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['schema'], 'project-governor-docs-manifest-v1')
            auth_entry = next(e for e in index['entries'] if e['path'] == 'src/auth.py')
            self.assertTrue(auth_entry['sensitive'])
            self.assertNotIn('sk-secretsecretsecretsecret', auth_entry['summary'])
            task_entry = next(e for e in index['entries'] if e['path'] == 'tasks/demo/ITERATION_PLAN.md')
            self.assertIn('task_history', task_entry['roles'])

            (project / 'docs' / 'architecture').mkdir(parents=True)
            (project / 'docs' / 'architecture' / 'ARCHITECTURE.md').write_text('# Architecture\n\nSystem boundaries.\n', encoding='utf-8')
            self.run_json([PY, str(ROOT / 'skills/context-indexer/scripts/build_context_index.py'), '--project', str(project), '--write'])
            index = json.loads((project / '.project-governor/context/CONTEXT_INDEX.json').read_text(encoding='utf-8'))
            architecture_entry = next(e for e in index['entries'] if e['path'] == 'docs/architecture/ARCHITECTURE.md')
            self.assertIn('architecture', architecture_entry['roles'])

            queried = self.run_json([PY, str(ROOT / 'skills/context-indexer/scripts/query_context_index.py'), '--project', str(project), '--request', 'auth login', '--route', 'risky_feature'])
            self.assertIn('confidence', queried)
            self.assertFalse(queried['read_all_initialization_docs'])
            self.assertIn('progressive_read_plan', queried)

    def test_context_query_returns_sections_and_filters_stale_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / '.project-governor').mkdir()
            (project / 'AGENTS.md').write_text('Project rules.\n', encoding='utf-8')
            (project / 'docs').mkdir()
            (project / 'docs/active.md').write_text(
                '# Active Guide\n\n## Checkout Redirect\n\nUse the hosted checkout redirect for payment handoff.\n',
                encoding='utf-8',
            )
            (project / 'docs/old.md').write_text(
                '# Old Guide\n\nStatus: superseded\n\n## Checkout Redirect\n\nLegacy embedded checkout notes.\n',
                encoding='utf-8',
            )
            self.run_json([PY, str(ROOT / 'skills/context-indexer/scripts/build_context_index.py'), '--project', str(project), '--write'])
            queried = self.run_json([
                PY,
                str(ROOT / 'skills/context-indexer/scripts/query_context_index.py'),
                '--project',
                str(project),
                '--request',
                'checkout redirect',
            ])
            paths = {item['path'] for item in queried['recommended_files']}
            section_headings = {item['heading'] for item in queried['recommended_sections']}
            avoided = {item['path'] for item in queried['avoid_docs']}
            self.assertIn('docs/active.md', paths)
            self.assertIn('Checkout Redirect', section_headings)
            self.assertNotIn('docs/old.md', paths)
            self.assertIn('docs/old.md', avoided)
            self.assertTrue(queried['context_compression']['full_documents_deferred'])

    def test_context_index_prefers_slots_for_generated_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / '.project-governor').mkdir()
            task = project / 'tasks/demo'
            task.mkdir(parents=True)
            (task / 'ITERATION_PLAN.slots.json').write_text(json.dumps({
                'template_id': 'iteration_plan_v1',
                'revision': 1,
                'user_request': 'Slot-only behavior should be indexed.',
                'existing_behavior': ['Variable slot content only.'],
            }), encoding='utf-8')
            (task / 'ITERATION_PLAN.md').write_text(
                '<!-- generated_from: iteration_plan_v1; source: ITERATION_PLAN.slots.json; revision: 1 -->\n'
                '# Iteration Plan\n\n'
                'Fixed template noise that should not drive summary.\n',
                encoding='utf-8',
            )
            self.run_json([PY, str(ROOT / 'skills/context-indexer/scripts/build_context_index.py'), '--project', str(project), '--write'])
            index = json.loads((project / '.project-governor/context/CONTEXT_INDEX.json').read_text(encoding='utf-8'))
            entry = next(e for e in index['entries'] if e['path'] == 'tasks/demo/ITERATION_PLAN.md')
            self.assertEqual(entry['generated_from'], 'iteration_plan_v1')
            self.assertEqual(entry['source_slots'], 'ITERATION_PLAN.slots.json')
            self.assertFalse(entry['template_content_indexed'])
            self.assertIn('Slot-only behavior should be indexed', entry['summary'])
            self.assertNotIn('Fixed template noise', entry['summary'])

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
            self.assertTrue((project / '.project-governor/state/COMMAND_LEARNINGS.json').exists())
            self.assertTrue((project / '.project-governor/state/MEMORY_HYGIENE.json').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
