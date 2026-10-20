"""Lightweight offline policy checks. No compilation, deployment, or external AI."""
import json
import pathlib
import re
import unittest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]


class PolicyTests(unittest.TestCase):
    def test_workflow_yaml(self):
        for p in (ROOT / '.github/workflows').glob('*.y*ml'):
            with self.subTest(file=p.name):
                d = yaml.load(p.read_text(), Loader=yaml.BaseLoader)
                self.assertIsInstance(d, dict)
                self.assertIn('on', d)
                self.assertIn('jobs', d)
    def test_no_automatic_heavy_or_publishing_entry(self):
        policy = json.loads((ROOT / '.github/automation/policy.json').read_text())
        for name in policy['manual_workflows']:
            with self.subTest(workflow=name):
                d = yaml.load((ROOT / '.github/workflows' / name).read_text(), Loader=yaml.BaseLoader)
                self.assertEqual(set(d['on']), {'workflow_dispatch'})
                for job in d['jobs'].values():
                    self.assertNotIn('workflow_run', str(job))
    def test_sync_does_not_chain_build_or_publish(self):
        d = yaml.load((ROOT / '.github/workflows/source-sync.yml').read_text(), Loader=yaml.BaseLoader)
        self.assertEqual(set(d['on']), {'schedule', 'workflow_dispatch'})
        self.assertEqual(set(d['jobs']), {'sync'})
        self.assertEqual(d['permissions'], {'contents': 'write'})
        text = (ROOT / '.github/workflows/source-sync.yml').read_text()
        for forbidden in ('repository-dispatch', 'gh workflow run', 'gh release', 'deploy-pages', 'workflow_call'):
            self.assertNotIn(forbidden, text)
    def test_policy_has_explicit_upstream_and_no_backfill(self):
        p = json.loads((ROOT / '.github/automation/policy.json').read_text())
        self.assertRegex(p['upstream_repository'], r'^[\w.-]+/[\w.-]+$')
        self.assertEqual(p['automatic_publish'], False)
        self.assertEqual(p['historical_backfill'], False)
        self.assertTrue(p['preserve_local_workflows'])


    def test_site_promotion_checks_existing_configuration_without_enabling_pages(self):
        path = ROOT / '.github/workflows/site-promote.yml'
        d = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
        self.assertEqual(d['jobs']['promote']['needs'], 'site-configuration')
        preflight = d['jobs']['site-configuration']
        self.assertEqual(preflight['permissions']['pages'], 'read')
        self.assertNotIn('environment', preflight)
        script = preflight['steps'][0]['run']
        self.assertIn('gh api', script)
        self.assertIn('.build_type', script)
        self.assertIn('!= workflow', script)
        self.assertNotIn('--method', script)
        self.assertNotIn('-X ', script)


if __name__ == '__main__':
    unittest.main()
