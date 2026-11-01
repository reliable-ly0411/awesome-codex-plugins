import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import check_catalog_snapshot as checker


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'README.md').write_text('## Community Plugins\n- [Example](https://github.com/owner/repo) - Description.\n')
        plugin = checker.generator.parse_plugins(self.root / 'README.md')[0]
        manifest = {'name': 'example', 'interface': {'composerIcon': './icon.svg'}}
        self.write('plugins/owner/repo/.codex-plugin/plugin.json', manifest)
        (self.root / 'plugins/owner/repo/icon.svg').write_text('<svg/>')
        self.catalog = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
                        'name': 'awesome-codex-plugins', 'version': '1.0.0',
                        'last_updated': '2020-01-01', 'total': 1,
                        'categories': [plugin['category']], 'plugins': [plugin]}
        self.market = {'name': 'awesome-codex-plugins', 'interface': {'displayName': 'Awesome Codex Plugins'},
                       'plugins': [checker.generator.build_marketplace_entry(plugin, manifest, './plugins/owner/repo', './plugins/owner/repo/icon.svg')]}
        self.save()

    def write(self, path, data):
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(data))

    def save(self):
        self.write('plugins.json', self.catalog)
        self.write('.agents/plugins/marketplace.json', self.market)

    def test_old_snapshot_is_read_only_and_offline(self):
        before = {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch.object(checker.generator, 'fetch_repo_archive', side_effect=AssertionError('network')):
            self.assertEqual(checker.check(self.root), [])
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_omission_is_not_grandfathered(self):
        self.catalog['plugins'] = []
        self.catalog['total'] = 0
        self.market['plugins'] = []
        self.save()
        self.assertTrue(any('missing from snapshot' in e for e in checker.check(self.root)))

    def test_metadata_policy_and_date_drift_fail(self):
        self.catalog['plugins'][0]['description'] = 'changed'
        self.catalog['total'] = 99
        self.catalog['last_updated'] = '2026-99-99'
        self.market['plugins'][0]['policy']['installation'] = 'FORCE'
        self.save()
        errors = checker.check(self.root)
        for marker in ('metadata differs', 'total', 'last_updated', 'Marketplace differs'):
            self.assertTrue(any(marker in e for e in errors), errors)

    def test_missing_icon_fails(self):
        (self.root / 'plugins/owner/repo/icon.svg').unlink()
        self.assertTrue(any('Missing local file' in e for e in checker.check(self.root)))

    def test_path_traversal_and_symlink_fail(self):
        for path in ('../outside', '/etc/passwd', 'plugins/../../outside', 'a\\b'):
            with self.assertRaises(ValueError):
                checker.local_file(self.root, path)
        (self.root / 'link').symlink_to(self.root / 'README.md')
        with self.assertRaises(ValueError):
            checker.local_file(self.root, 'link')

    def test_unsafe_icon_reference_fails(self):
        self.write('plugins/owner/repo/.codex-plugin/plugin.json',
                   {'name': 'example', 'interface': {'composerIcon': '/icon.svg'}})
        self.assertTrue(any('Unsafe icon path' in e for e in checker.check(self.root)))

    def test_catalog_order_is_checked(self):
        with (self.root / 'README.md').open('a') as stream:
            stream.write('- [Second](https://github.com/owner/second) - Second.\n')
        second = checker.generator.parse_plugins(self.root / 'README.md')[1]
        self.write('plugins/owner/second/.codex-plugin/plugin.json', {'name': 'second'})
        self.catalog['plugins'].insert(0, second)
        self.catalog['total'] = 2
        self.save()
        self.assertTrue(any('order differs' in e for e in checker.check(self.root)))

    def test_duplicate_and_extra_entry_fail(self):
        self.catalog['plugins'] *= 2
        self.save()
        self.assertTrue(any('Duplicate' in e for e in checker.check(self.root)))


if __name__ == '__main__':
    unittest.main()
