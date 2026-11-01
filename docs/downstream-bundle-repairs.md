# Downstream bundle metadata repairs

These changes repair mirrored catalog metadata only. They do not change plugin
execution code, grant admission, or override source scans. Upstream generation
may replace mirrored files; revalidate provenance before reapplying them.

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
