import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('generator', Path(__file__).resolve().parents[1] / 'scripts/generate_plugins_json.py')
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)

class LocalCatalogTests(unittest.TestCase):
    def test_local_generation_is_offline_and_date_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / 'plugins/owner/repo/.codex-plugin'
            bundle.mkdir(parents=True)
            (bundle / 'plugin.json').write_text(json.dumps({'name':'example', 'interface':{'displayName':'Example'}}))
            readme = root / 'README.md'
            readme.write_text('## Community Plugins\n### Tools\n- [Example](https://github.com/owner/repo) - Example plugin.\n')
            output = root / 'plugins.json'
            output.write_text(json.dumps({'last_updated':'2026-01-01','plugins':[]}))
            market = root / 'market.json'
            with patch.multiple(g, README=readme, OUTPUT=output, MARKETPLACE_OUTPUT=market, PLUGINS_ROOT=root/'plugins'), patch.object(g,'fetch_repo_archive',side_effect=AssertionError('network forbidden')):
                g.main(local=True)
                first = (output.read_bytes(),market.read_bytes())
                g.main(local=True)
                self.assertEqual(first,(output.read_bytes(),market.read_bytes()))
                self.assertEqual(json.loads(output.read_text())['last_updated'],'2026-01-01')

    def test_missing_bundle_is_a_hard_failure(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(g,'PLUGINS_ROOT',Path(tmp)):
            with self.assertRaises(ValueError):
                g.local_plugin_bundle({'owner':'owner','repo':'missing','name':'Missing'})

    def test_ambiguous_bundle_is_a_hard_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ['one','two']:
                p=root/'owner/repo'/name/'.codex-plugin'
                p.mkdir(parents=True)
                (p/'plugin.json').write_text(json.dumps({'name':'same'}))
            with patch.object(g,'PLUGINS_ROOT',root), self.assertRaises(ValueError):
                g.local_plugin_bundle({'owner':'owner','repo':'repo','name':'same'})

if __name__ == '__main__':
    unittest.main()
