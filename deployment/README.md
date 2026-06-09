# Deployment

Purpose: deployment notes for sovereign edge clusters, hybrid cloud, and air-gapped operation.

Architecture: each sovereign node runs local services, storage, audit logging, and dashboards. Coalition sharing uses signed, scoped event summaries and immutable audit relay indexes.

Security considerations:
- Zero-trust networking and mTLS for event transport.
- Federated identity and sovereign key ownership.
- Hardware-backed signing in production.
- Air-gapped operation should use offline event bundles and delayed audit relay synchronization.
