# Upstream automation policy

- Daily and manual source sync follows `hashgraph-online/awesome-codex-plugins:main` into `sync-only/upstream-main`. It does not build or publish.
- Local workflows and maintenance policy are retained; conflicting upstream changes stop rather than force-push.
- Existing historical tags and releases are never recreated or overwritten. Baseline deployment does not backfill releases.
- No recognized new upstream formal release means no automatic heavyweight build or publication. A source commit, website rebuild, tag alone, or dependency update is not a release signal.
- Manual build and promotion remain separate where the repository has a real deliverable. Repositories without a build/publisher do not gain a fabricated release route.
- Lightweight read-only safety checks remain enabled. This policy does not enable third-party dispatch, credentials, external AI, or repository security settings.
- Website repositories sync into a non-publishing source branch. Publication requires an explicit manual promotion of verified build artifacts; no automatic merge into the live Pages source.

## Manual website operations

Run `deploy.yml` on the default branch with the full source commit (including a reviewed source-sync commit). This builds only and retains `site-candidate` for 30 days. Record the run ID, source SHA and artifact.tar SHA256 from the summary. Run `site-promote.yml` separately with those exact identities to deploy the same bytes without rebuilding. Existing Pages source/environment protections remain authoritative; this change does not alter their settings. Expired or inconsistent artifacts are rejected, not silently rebuilt.

External curation / cross-repository dispatcher implementations are retained as non-executing reference files under inactive-reference. Their workflow interfaces only explain that these actions are disabled in this fork; no token or content is sent. Restoring external communications requires a separately reviewed policy. Existing read-only contribution/security checks remain unchanged.

Security scanner workflows and their publisher scripts incorporate the existing sync/security candidate caed325c1df045693dafcf26421a3283ea264bea's fail-closed score >= 80 and high/critical gates. Scans explicitly use online:false/submission_enabled:false; no external agent or registry submission is enabled. Claim/registry notices are manual-only. Generated catalog checks are read-only and fail when stale instead of auto-committing.

Pages promotion first reads the existing configuration and refuses to deploy unless its build type is already `workflow`. It never enables Pages, changes its source, or creates credentials.
The Pages settings were observed disabled (source branch `None`) on 2026-10-20. Manual candidate builds remain usable; publication is blocked until Pages enablement is separately approved and configured.
