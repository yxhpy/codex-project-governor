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

class GPT55AutoOrchestrationTest(unittest.TestCase):
    def run_json(self, args):
        proc = subprocess.run(args, text=True, capture_output=True, check=True, timeout=15)
        return json.loads(proc.stdout)

    def test_micro_patch_uses_fast_path_without_subagents(self):
        data = self.run_json([PY, str(ROOT / 'skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py'), str(ROOT / 'examples/gpt55-runtime-micro-patch.json')])
        self.assertEqual(data['route'], 'micro_patch')
        self.assertEqual(data['subagent_mode'], 'none')
        self.assertEqual(data['subagents'], [])
        self.assertFalse(data['context_budget']['read_all_initialization_docs'])
        self.assertIn('route-guard', data['skill_sequence'])

    def test_docs_typo_uses_light_path_without_subagents(self):
        data = self.run_json([PY, str(ROOT / 'skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py'), '--request', 'fix a typo in README'])
        self.assertEqual(data['route'], 'docs_only')
        self.assertEqual(data['quality_gate'], 'light')
        self.assertEqual(data['subagent_mode'], 'none')
        self.assertEqual(data['subagents'], [])
        self.assertEqual(data['model_plan']['main_model'], 'gpt-5.4-mini')
        self.assertEqual(data['skill_sequence'], ['direct-edit', 'quality-gate', 'merge-readiness'])
        self.assertFalse(data['evidence_required'])
        self.assertFalse(data['state_policy']['session_start'])

    def test_standard_feature_uses_context_index_and_subagents(self):
        data = self.run_json([PY, str(ROOT / 'skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py'), str(ROOT / 'examples/gpt55-runtime-standard-feature.json')])
        self.assertEqual(data['route'], 'standard_feature')
        self.assertIn('context-indexer', data['skill_sequence'])
        self.assertIn('engineering-standards-governor', data['skill_sequence'])
        self.assertIn('context-scout', data['subagents'])
        self.assertEqual(data['model_plan']['main_model'], 'gpt-5.5')
        self.assertEqual(data['model_plan']['scout_model'], 'gpt-5.4-mini')
        self.assertEqual(data['context_retrieval']['docs_manifest'], '.project-governor/context/DOCS_MANIFEST.json')
        self.assertEqual(data['context_retrieval']['query_granularity'], 'section')
        self.assertTrue(data['quality_rules']['prefer_section_ranges_before_full_docs'])
        self.assertIn('route_doc_pack', data)

    def test_risky_feature_uses_strict_high_reasoning(self):
        data = self.run_json([PY, str(ROOT / 'skills/gpt55-auto-orchestrator/scripts/select_runtime_plan.py'), str(ROOT / 'examples/gpt55-runtime-risky-feature.json')])
        self.assertEqual(data['route'], 'risky_feature')
        self.assertEqual(data['quality_gate'], 'strict')
        self.assertEqual(data['model_plan']['reasoning_effort'], 'high')
        self.assertIn('risk-scout', data['subagents'])
        self.assertEqual(data['subagent_mode'], 'required')

    def test_context_index_build_and_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / '.project-governor').mkdir()
            (project / 'AGENTS.md').write_text('Project Governor rules for dashboard widgets.\n', encoding='utf-8')
            (project / 'src/components').mkdir(parents=True)
            (project / 'src/components/DashboardWidget.tsx').write_text('export function DashboardWidget() { return null }\n', encoding='utf-8')
            (project / 'docs/conventions').mkdir(parents=True)
            (project / 'docs/conventions/PATTERN_REGISTRY.md').write_text('Dashboard widget card pattern.\n', encoding='utf-8')
            built = self.run_json([PY, str(ROOT / 'skills/context-indexer/scripts/build_context_index.py'), '--project', str(project), '--write'])
            self.assertEqual(built['status'], 'written')
            self.assertTrue((project / '.project-governor/context/DOCS_MANIFEST.json').exists())
            queried = self.run_json([PY, str(ROOT / 'skills/context-indexer/scripts/query_context_index.py'), '--project', str(project), '--request', 'dashboard widget'])
            paths = {item['path'] for item in queried['recommended_files']}
            self.assertIn('src/components/DashboardWidget.tsx', paths)
            self.assertFalse(queried['read_all_initialization_docs'])
            self.assertIn('must_read_sections', queried)

    def test_context_index_memory_search_auto_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / '.project-governor').mkdir()
            (project / 'docs/memory').mkdir(parents=True)
            (project / 'docs/memory/PROJECT_MEMORY.md').write_text('Checkout flow uses Stripe redirect based on ADR-0003.\n', encoding='utf-8')
            (project / 'docs/decisions').mkdir(parents=True)
            (project / 'docs/decisions/ADR-0003-checkout.md').write_text('Use Stripe redirect checkout for hosted payment pages.\n', encoding='utf-8')
            (project / 'tasks/2026-04-28-checkout').mkdir(parents=True)
            (project / 'tasks/2026-04-28-checkout/ITERATION_PLAN.md').write_text('Investigate checkout redirect regression.\n', encoding='utf-8')
            (project / 'src').mkdir()
            (project / 'src/checkout.py').write_text('def checkout():\n    return True\n', encoding='utf-8')
            data = self.run_json([
                PY,
                str(ROOT / 'skills/context-indexer/scripts/query_context_index.py'),
                '--project',
                str(project),
                '--request',
                'checkout redirect decision history',
                '--memory-search',
                '--auto-build',
            ])
            self.assertTrue(data['auto_built'])
            self.assertEqual(data['search_mode'], 'governance_memory')
            self.assertFalse(data['raw_chat_history_search'])
            self.assertIn('progressive_read_plan', data)
            paths = {item['path'] for item in data['recommended_files']}
            self.assertIn('docs/memory/PROJECT_MEMORY.md', paths)
            self.assertIn('docs/decisions/ADR-0003-checkout.md', paths)
            self.assertNotIn('src/checkout.py', paths)
            text_proc = subprocess.run([
                PY,
                str(ROOT / 'skills/context-indexer/scripts/query_context_index.py'),
                '--project',
                str(project),
                '--request',
                'checkout redirect decision history',
                '--memory-search',
                '--format',
                'text',
            ], text=True, capture_output=True, check=True, timeout=15)
            self.assertIn('mode: governance_memory', text_proc.stdout)
            self.assertIn('docs/memory/PROJECT_MEMORY.md', text_proc.stdout)

    def test_clean_reinstall_apply_latest_mode_for_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / 'app'
            project.mkdir()
            (project / '.project-governor').mkdir()
            (project / 'AGENTS.md').write_text('Project Governor initialized.\n', encoding='utf-8')
            (project / 'src').mkdir()
            (project / 'src/main.py').write_text('print("hi")\n', encoding='utf-8')
            data = self.run_json([PY, str(ROOT / 'skills/clean-reinstall-manager/scripts/apply_latest_runtime_mode.py'), '--path', str(project), '--plugin-root', str(ROOT), '--apply'])
            self.assertEqual(data['status'], 'project_runtime_mode_ready')
            self.assertTrue((project / '.project-governor/runtime/GPT55_RUNTIME_MODE.json').exists())
            self.assertTrue((project / '.project-governor/context/CONTEXT_INDEX.json').exists())
            self.assertFalse((project / '.codex/agents').exists())

if __name__ == '__main__':
    unittest.main(verbosity=2)
