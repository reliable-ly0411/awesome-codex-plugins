# Downstream bundle metadata repairs

These changes repair mirrored catalog metadata only. They do not change plugin
execution code, grant admission, or override source scans. Online generation reapplies only the bounded missing-field repairs below.
Existing upstream values win; license fields require the bundled license evidence.
The reviewed icon derivative is retained only when both derivative and source
match the exact reviewed SHA-256 hashes; changed artwork requires fresh review.

## Provenance

- `Kanevry/session-orchestrator`: repository URL follows the mirrored source
  identity; `MIT` is copied from the bundled `LICENSE`.
- `boshu2/agentops`: repository URL follows the mirrored source identity;
  `Apache-2.0` is copied from the bundled `LICENSE`.
- `ndycode/codex-multi-auth` and `ndycode/oc-chatgpt-multi-auth`: repository URLs
  follow the mirrored source identities; `MIT` is copied from each bundled
  `LICENSE`. Display names preserve the existing manifest `name`, and short
  descriptions copy its existing `description` without adding claims.
- `runtypelabs/skills`: interface display name copies the existing top-level
  `displayName`; short description copies the existing `description`.
- `IgorVaryvoda/image-optimization-skill`: composer icon uses an additional
  lossless WebP encoding of the existing PNG. Dimensions and decoded 8-bit RGBA
  bytes are identical; the original PNG is retained. The new icon is 19,962 bytes
  and meets the unchanged 50 KiB limit.

The remaining missing icons, missing interface definitions, and oversized icons
are not repaired by inventing branding, changing source behavior, removing
catalog entries, or weakening validation. Scanner findings remain independently
blocking. A metadata repair is not a security audit pass.

## Snapshot validation versus online refresh

`python3 scripts/check_catalog_snapshot.py` checks the committed README, catalog,
marketplace, manifests, and icon paths without network access or writes. It checks
all README entries, duplicates, counts, ordering, metadata, policies, and safe local
paths; missing bundles are errors, not an allowlist. Snapshot dates are validated
as dates rather than compared to the clock. Bundle and source security checks stay
independent and unchanged.

`python3 scripts/generate_plugins_json.py` remains the explicit online refresh
command. It fetches mutable upstream HEADs and writes a new reviewed source
snapshot; it is not a reproducibility check. The prior CI step refreshed 1,122
files in the merge-head run, then rejected the drift. No automated publication or
cross-repository contribution is introduced by separating these operations.
