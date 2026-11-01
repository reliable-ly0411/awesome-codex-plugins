"""Online refresh must not erase bounded provenance-backed metadata repairs."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('generator', ROOT / 'scripts/generate_plugins_json.py')
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)


class ReviewedNormalizationTests(unittest.TestCase):
    def test_license_requires_evidence_and_preserves_upstream_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plugin = {'owner': 'Kanevry', 'repo': 'session-orchestrator'}
            manifest = {}
            g.normalize_reviewed_metadata(manifest, plugin, root)
            self.assertNotIn('license', manifest)
            (root / 'LICENSE').write_text('MIT License')
            g.normalize_reviewed_metadata(manifest, plugin, root)
            self.assertEqual(manifest['license'], 'MIT')
            manifest['license'] = 'other-reviewed-license'
            manifest['repository'] = 'https://example.org/new-home'
            g.normalize_reviewed_metadata(manifest, plugin, root)
            self.assertEqual(manifest['license'], 'other-reviewed-license')
            self.assertEqual(manifest['repository'], 'https://example.org/new-home')

    def test_unknown_source_not_normalized(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'LICENSE').write_text('MIT License')
            manifest = {'name': 'Example'}
            g.normalize_reviewed_metadata(manifest, {'owner': 'unknown', 'repo': 'source'}, Path(tmp))
            self.assertEqual(manifest, {'name': 'Example'})

    def test_interface_copies_existing_values_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin = {'owner': 'runtypelabs', 'repo': 'skills'}
            manifest = {'name': 'skills', 'displayName': 'Existing Name', 'description': 'Existing text'}
            g.normalize_reviewed_metadata(manifest, plugin, Path(tmp))
            self.assertEqual(manifest['interface'], {'displayName': 'Existing Name', 'shortDescription': 'Existing text'})
            manifest['interface']['displayName'] = 'Updated upstream'
            g.normalize_reviewed_metadata(manifest, plugin, Path(tmp))
            self.assertEqual(manifest['interface']['displayName'], 'Updated upstream')

    def test_icon_requires_exact_reviewed_original_and_derivative(self):
        source = ROOT / 'plugins/IgorVaryvoda/image-optimization-skill'
        data = g.retained_reviewed_icon(source)
        self.assertIsNotNone(data)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '.claude-plugin').mkdir()
            original = root / '.claude-plugin/icon.png'
            original.write_bytes((source / '.claude-plugin/icon.png').read_bytes())
            manifest = {'interface': {'composerIcon': './.claude-plugin/icon.png'}}
            g.restore_reviewed_icon(manifest, root, data)
            self.assertEqual(manifest['interface']['composerIcon'], './.claude-plugin/icon.catalog.webp')
            (root / '.claude-plugin/icon.catalog.webp').write_bytes(b'changed')
            self.assertIsNone(g.retained_reviewed_icon(root))
            original.write_bytes(b'changed original')
            manifest['interface']['composerIcon'] = './.claude-plugin/icon.png'
            g.restore_reviewed_icon(manifest, root, data)
            self.assertEqual(manifest['interface']['composerIcon'], './.claude-plugin/icon.png')
