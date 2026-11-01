# Upstream automation policy

- Daily and manual source sync follows `hashgraph-online/awesome-codex-plugins:main` into `sync-only/upstream-main`. It does not build or publish.
- Reviewed downstream policy paths are retained from a pinned default-branch commit. Only conflicts inside the explicit allowlist are resolved with that policy; all other source conflicts abort and list their paths. Pushes are normal, never forced.
- Existing historical tags and releases are never recreated or overwritten. Baseline deployment does not backfill releases.
- No recognized new upstream formal release means no automatic heavyweight build or publication. A source commit, website rebuild, tag alone, or dependency update is not a release signal.
- Manual build and promotion remain separate where the repository has a real deliverable. Repositories without a build/publisher do not gain a fabricated release route.
- Lightweight read-only safety checks remain enabled. This policy does not enable third-party dispatch, credentials, external AI, or repository security settings.
- Website repositories sync into a non-publishing source branch. Publication requires an explicit manual promotion of verified build artifacts; no automatic merge into the live Pages source.

## Manual website operations

Run `deploy.yml` on the default branch with the full source commit (including a reviewed source-sync commit). This builds only and retains `site-candidate` for 30 days. Record the run ID, source SHA and artifact.tar SHA256 from the summary. Run `site-promote.yml` separately with those exact identities to deploy the same bytes without rebuilding. Existing Pages source/environment protections remain authoritative; this change does not alter their settings. Expired or inconsistent artifacts are rejected, not silently rebuilt.

External curation / cross-repository dispatcher implementations are retained as non-executing reference files under inactive-reference. Their workflow interfaces only explain that these actions are disabled in this fork; no token or content is sent. Restoring external communications requires a separately reviewed policy. Existing read-only contribution/security checks remain unchanged.

Security scanner workflows and their publisher scripts incorporate the existing sync/security candidate caed325c1df045693dafcf26421a3283ea264bea's fail-closed score >= 80 and high/critical gates. Scans explicitly use online:false/submission_enabled:false; no external agent or registry submission is enabled. Claim/registry notices are disabled in this fork; the previous interface is retained as an inactive reference. Generated catalog checks are read-only and fail when stale instead of auto-committing.

Pages promotion first reads the existing configuration and refuses to deploy unless its build type is already `workflow`. It never enables Pages, changes its source, or creates credentials.
The Pages settings were observed disabled (source branch `None`) on 2026-10-20. Manual candidate builds remain usable; publication is blocked until Pages enablement is separately approved and configured.

## Sync-only direction and conflict handling

This fork only receives upstream source. Do not prepare or submit upstream pull
requests, comments, code, registry notices, or cross-repository dispatches. Existing
branches, commits and draft PRs remain intact. Contribution validation describes
catalog safety checks inside this fork; it is not authorization to contribute
upstream, and failing checks must not be disabled to make synchronization green.

`downstream_repository` is the only permitted push destination. The script checks
every origin push URL and requires the configured non-default source branch before
any merge and again before a normal push. It never pushes main, tags or upstream.

The workflow snapshots the trusted default-branch policy SHA before checking out
the existing source branch. `preserve_local_paths` is an explicit reviewed
allowlist, not a blanket source-conflict override. Upstream additions and changes
under those paths are held and reported, including newly introduced workflows.
Other source files use an ordinary two-parent merge that retains both histories.
The latest trusted policy also refreshes an existing source branch when its source
is already current. Remote lookup failures stop instead of being mistaken for a
missing branch. No sync step builds, publishes, merges a PR or submits upstream.

Policy and source candidates are only activated after a separately authorized
merge into the default branch. A draft fix does not repair the currently scheduled
default-branch job by itself. This task does not authorize merging or publishing.

The Codex allowlist also retains the two check-result publishers, their regression
tests and the two scanner policy guides. Those files carry the existing blocking
high/critical policy; upstream currently describes severities as advisory. Holding
them keeps reports and documentation aligned with the retained scanner gates.
Upstream changes to these held paths require a separate downstream policy review.

Existing draft PR #1 targets this fork's main and remains unchanged. It is a source
sync candidate, not an upstream submission. Its catalog scanner and plugin-bundle
failures remain real blockers; this automation fix does not clear those results.
