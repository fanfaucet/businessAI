# Governance and Audit

Purpose: audit-first workflows, immutable recommendation logs, explainability reports, transparency dashboards, and policy replay support.

Architecture: recommendations are written to append-only logs with rationale, confidence, affected constraints, projected tradeoffs, and human-review state.

Security: audit records reference sovereign scopes and policy versions; raw protected datasets should remain in jurisdictional stores.
