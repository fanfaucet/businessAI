# Heritage Stack™ Governance Kernel

Purpose: implement Zero-Damage Mandate and Human-in-the-Loop control loops as inspectable kernel logic for high-stakes or external-facing actions.

## Architecture

- `ZeroDamageMandate` rejects requests that attempt to bypass human authority, centralize sovereign authority, hide objectives, merge protected datasets, or mislabel destructive actions.
- `HumanApprovalGate` requires explicit human approval records for destructive, external-facing, high-stakes, or system-state-transition actions.
- `WatchdogDaemon` enforces signature quorum checks before critical actions. The repository includes a deterministic SHA-256 verifier for tests and offline scaffolding; production deployments should bind the same interface to hardware-backed Ed25519 verification and sovereign-owned keys.
- `ZYXKernel` composes the mandate, HITL gate, and Watchdog checks into a single governance decision.

## Security considerations

This package does not execute requested actions. It only evaluates whether a proposed action is allowed, denied, or blocked pending approval/signature evidence. The design preserves the advisory-only posture used throughout AnnabanAI/AetherOS.
