#!/usr/bin/env python3
"""Check committed catalog consistency without fetching, executing, or writing bundles.

Online refresh remains generate_plugins_json.py. This validates the reviewed local
snapshot, not today's mutable upstream HEAD or today's date. Bundle admission and
security scans are separate, unchanged checks.
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path, PurePosixPath
import sys

import generate_plugins_json as generator

ROOT = Path(__file__).resolve().parents[1]


def local_file(root: Path, relative: str) -> Path:
    """Reject traversal, symlinks, absolute paths, and missing files."""
    if not isinstance(relative, str) or not relative or '\\' in relative:
        raise ValueError(f"Invalid local path: {relative!r}")
    path = PurePosixPath(relative)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError(f"Unsafe local path: {relative}")
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"Symlink not allowed: {relative}")
    if not current.is_file():
        raise ValueError(f"Missing local file: {relative}")
    return current


def check(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        parsed = generator.parse_plugins(root / 'README.md')
        for plugin in parsed:
            if plugin.get('_local_bundle') == 'true':
                local_file(root, f"plugins/{plugin['owner']}/{plugin['repo']}/.codex-plugin/plugin.json")
        readme = [p for p in parsed if p.get('_local_bundle') != 'true']
        catalog = json.loads(local_file(root, 'plugins.json').read_text())
        market = json.loads(local_file(root, '.agents/plugins/marketplace.json').read_text())
        entries = catalog['plugins']
        if not isinstance(entries, list) or not isinstance(market['plugins'], list):
            raise ValueError('Catalog and marketplace plugins must be arrays')
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return [f'Cannot read snapshot: {exc}']
    expected_header = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
                       'name': 'awesome-codex-plugins', 'version': '1.0.0'}
    for key, value in expected_header.items():
        if catalog.get(key) != value:
            errors.append(f'Catalog {key} is inconsistent')
    if set(catalog) != set(expected_header) | {'last_updated', 'total', 'categories', 'plugins'}:
        errors.append('Unexpected catalog fields')
    date = catalog.get('last_updated')
    try:
        if not isinstance(date, str) or datetime.date.fromisoformat(date).isoformat() != date:
            raise ValueError()
    except ValueError:
        errors.append('last_updated must be a valid YYYY-MM-DD snapshot date')
    if catalog.get('total') != len(entries):
        errors.append('Catalog total does not match entries')
    if catalog.get('categories') != sorted({p['category'] for p in readme}):
        errors.append('Catalog categories differ from README')

    def identity(p):
        return (p['owner'], p['repo'], p['name'])

    expected = {identity(p): p for p in readme}
    actual_ids = []
    rebuilt = []
    for entry in entries:
        try:
            key = identity(entry)
            if key in actual_ids:
                errors.append(f'Duplicate catalog entry: {key}')
            actual_ids.append(key)
            plugin = expected.get(key)
            if plugin is None:
                errors.append(f'Catalog entry absent from README: {key}')
                continue
            public = {k: v for k, v in plugin.items() if not k.startswith('_')}
            url = entry.get('install_url', '')
            prefix = f"https://raw.githubusercontent.com/{plugin['owner']}/{plugin['repo']}/HEAD/"
            suffix = '/.codex-plugin/plugin.json'
            if url == prefix + '.codex-plugin/plugin.json':
                subpath = ''
            elif isinstance(url, str) and url.startswith(prefix) and url.endswith(suffix):
                subpath = url[len(prefix):-len(suffix)]
                if not subpath or PurePosixPath(subpath).is_absolute() or '..' in PurePosixPath(subpath).parts or '\\' in subpath:
                    raise ValueError(f'Unsafe upstream manifest subpath: {url}')
            else:
                raise ValueError(f'Invalid install_url: {url}')
            public['install_url'] = generator.build_raw_manifest_url(plugin, subpath)
            if entry != public:
                errors.append(f'Catalog metadata differs from README: {key}')
            bundle = f"./plugins/{plugin['owner']}/{plugin['repo']}"
            if plugin.get('_mirror_subpath') == 'true' and subpath:
                bundle += '/' + subpath
            manifest = json.loads(local_file(root, bundle + '/.codex-plugin/plugin.json').read_text())
            interface = manifest.get('interface', {})
            icon = None
            if isinstance(interface, dict):
                ref = interface.get('composerIcon') or interface.get('logo')
                if isinstance(ref, str) and ref.strip():
                    if PurePosixPath(ref).is_absolute() or '..' in PurePosixPath(ref).parts or '\\' in ref:
                        raise ValueError(f'Unsafe icon path: {ref}')
                    rel = generator.normalize_relative_path(ref)
                    local_file(root, bundle + '/' + rel)
                    icon = bundle + '/' + rel
            rebuilt.append(generator.build_marketplace_entry(plugin, manifest, bundle, icon))
        except (ValueError, KeyError, TypeError, OSError) as exc:
            errors.append(f'Invalid snapshot entry: {exc}')
    for key in expected:
        if key not in actual_ids:
            errors.append(f'README entry missing from snapshot: {key[0]}/{key[1]} ({key[2]})')
    if actual_ids != [identity(p) for p in readme if identity(p) in actual_ids]:
        errors.append('Catalog order differs from README')
    expected_market = {'name': 'awesome-codex-plugins',
                       'interface': {'displayName': 'Awesome Codex Plugins'}, 'plugins': rebuilt}
    if market != expected_market:
        errors.append('Marketplace differs from committed manifests/README (including order, paths, icons, policy)')
    return errors


if __name__ == '__main__':
    failures = check()
    for failure in failures:
        print(f'ERROR: {failure}', file=sys.stderr)
    if failures:
        sys.exit(1)
    print('Committed catalog snapshot is consistent')
