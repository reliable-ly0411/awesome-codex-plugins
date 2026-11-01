"""Provenance checks for the bounded downstream manifest repairs."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class BundleRepairTests(unittest.TestCase):
    def test_license_fields_match_bundled_license_text(self):
        for slug, license_id, marker in (
            ('Kanevry/session-orchestrator', 'MIT', 'MIT License'),
            ('boshu2/agentops', 'Apache-2.0', 'Apache License'),
            ('ndycode/codex-multi-auth', 'MIT', 'MIT License'),
            ('ndycode/oc-chatgpt-multi-auth', 'MIT', 'MIT License'),
        ):
            with self.subTest(slug=slug):
                directory = ROOT / 'plugins' / slug
                manifest = json.loads((directory / '.codex-plugin/plugin.json').read_text())
                self.assertEqual(manifest['license'], license_id)
                self.assertIn(marker, (directory / 'LICENSE').read_text())
                self.assertEqual(manifest['repository'], 'https://github.com/' + slug)

    def test_interface_text_comes_from_existing_manifest_fields(self):
        for slug in ('ndycode/codex-multi-auth', 'ndycode/oc-chatgpt-multi-auth', 'runtypelabs/skills'):
            with self.subTest(slug=slug):
                manifest = json.loads((ROOT / 'plugins' / slug / '.codex-plugin/plugin.json').read_text())
                self.assertEqual(manifest['interface']['shortDescription'], manifest['description'])
                self.assertEqual(manifest['interface']['displayName'], manifest.get('displayName', manifest['name']))

    def test_icon_is_bounded_and_original_retained(self):
        directory = ROOT / 'plugins/IgorVaryvoda/image-optimization-skill'
        manifest = json.loads((directory / '.codex-plugin/plugin.json').read_text())
        self.assertEqual(manifest['interface']['composerIcon'], './.claude-plugin/icon.catalog.webp')
        self.assertTrue((directory / '.claude-plugin/icon.png').is_file())
        self.assertLessEqual((directory / '.claude-plugin/icon.catalog.webp').stat().st_size, 50 * 1024)

if __name__ == '__main__':
    unittest.main()
