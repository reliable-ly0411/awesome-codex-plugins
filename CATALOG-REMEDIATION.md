# Catalog remediation

The 2026-11-16 repair changes mirrored catalog metadata only. Original plugin runtime code and original artwork are retained. Missing or oversized composer icons use a small, original neutral code glyph rather than misrepresenting a third-party logo. Missing names and descriptions come from the existing README/manifest. License identifiers are taken from the bundled LICENSE, not inferred from the catalog license.

This does not clear source-repository scanner findings. High/critical thresholds remain blocking. No plugin is installed or executed by these repairs.

Affected bundles:

- plugins/IgorVaryvoda/image-optimization-skill
- plugins/JeongJaeSoon/agent-guard
- plugins/Kanevry/session-orchestrator
- plugins/Kloudedge-apex/receipts-collector
- plugins/NotNull92/hera-agent-godot
- plugins/aklofas/kicad-happy
- plugins/alirezarezvani/claude-skills
- plugins/ariaxhan/kernel-claude
- plugins/avivsinai/agent-message-queue
- plugins/boshu2/agentops
- plugins/danjdewhurst/story-skills
- plugins/minsu0707/auto-pilot
- plugins/ndycode/codex-multi-auth
- plugins/ndycode/oc-chatgpt-multi-auth
- plugins/negm17111995/mcp-server
- plugins/ooples/token-optimizer-mcp
- plugins/panewslab/skills
- plugins/plori-ai/codex-plugin
- plugins/posteverywhere/codex-plugin
- plugins/prekuter/dryforge
- plugins/reliable-ly0411/babeldoc-pdf-translate
- plugins/runtypelabs/skills
- plugins/s977043/river-review
- plugins/tashfeenahmed/AgentDomains-skill
- plugins/tuantqse90/moltnode-mcp
- plugins/useorgx/orgx-codex-plugin
- plugins/villagesql/villagesql-skills
- plugins/vishal2612200/agentpack
- plugins/yagizdo/quiver
- plugins/yylo-dev/yylo

## Reproducible catalog checks

`python3 scripts/generate_plugins_json.py --local` rebuilds metadata from the committed reviewed bundles and preserves the prior catalog date. Missing/ambiguous local bundles fail rather than silently disappearing. Normal generation without `--local` remains the explicit upstream refresh operation. CI consistency checking no longer imports mutable third-party HEADs.

Maintainer Mode was moved to an unavailable-reference section after its API and archive returned 404 and no local bundle existed. Its link remains visible; no runtime bundle was deleted.

Scanner jobs now retain JSON finding details and the exact source commit even on failure. Their score and high/critical severity gates, source scope, and disabled online submission remain unchanged. The six failing third-party sources still require rule-level review; no finding is suppressed by this patch.
