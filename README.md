# :earth_americas: GDP dashboard template

A simple Streamlit app showing the GDP of different countries in the world.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://gdp-dashboard-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

## AnnabanAI Cognitive Kernel v1

This repository now includes a modular AnnabanAI orchestration runtime alongside the
original GDP dashboard. The implementation favors deterministic local execution by
default while keeping OpenAI/xAI-compatible providers available through the provider
router when credentials are configured.

### Architecture reasoning

The runtime is organized as a single-process cognitive kernel instead of a distributed
microservice system. This keeps the Streamlit app responsive and deployable while still
adding production-grade boundaries:

- `AnnabanRuntime` is the runtime spine that coordinates sentiment, agents, provider
  routing, memory persistence, audit mirroring, and telemetry.
- Memory persistence now depends on a `MemoryBackend` protocol so SQLite can be replaced
  by PostgreSQL or immutable audit backends without rewriting the runtime spine.
- `ProviderRouter` normalizes OpenAI, xAI, and fallback responses behind one inference
  contract with retries, latency metrics, token accounting, and graceful degradation.
- `MemoryManager` treats SQLite as the source of truth and stores canonical
  `InteractionRecord` rows plus deterministic runtime events transactionally.
- `AuditManager` writes an append-only JSONL mirror with chained `previous_hash`,
  `payload_hash`, and `event_hash` continuity for replay and forensic inspection.
- `SentimentEngine` fuses DistilBERT and TextBlob when available and falls back to a
  neutral signal when optional local NLP dependencies are unavailable.
- Planner, Reviewer, Executor, and Audit agents run as deterministic subagents before
  provider inference, creating an extensible orchestration contract.

### Migration steps

1. Install app dependencies with `pip install -r requirements.txt`.
2. Run `python -m unittest discover -s tests -v` to verify the local fallback runtime.
3. Start the dashboard with `streamlit run streamlit_app.py`.
4. Use the **AnnabanAI orchestration console** to send prompts through the runtime.
5. Inspect SQLite-backed memory in `annabanai_outputs/runtime_state.db` and the JSONL
   audit mirror in `annabanai_outputs/interactions.jsonl`.
6. To enable hosted inference, set `OPENAI_API_KEY` or `XAI_API_KEY`, then choose the
   corresponding provider route from the Streamlit console.

### Risks and performance improvements

- DistilBERT initialization can be slow on CPU-only machines; keep fallback sentiment
  enabled for UI responsiveness or preload the model in a warm-up task.
- SQLite is appropriate for local deterministic orchestration; high-concurrency
  deployments should move the `MemoryManager` contract to PostgreSQL.
- Provider calls are isolated and retry-aware, but hosted model latency remains external;
  production deployments should add circuit-breaker thresholds and request queues.
- The agent framework is intentionally local and deterministic; parallel fanout can be
  added with `asyncio` once agents become I/O-bound.

## Federated Maritime Governance Stack Scaffold

This repository also includes a scaffold for the AnnabanAI / AetherOS / AnnabanOS
federated maritime governance stack. The scaffold is intentionally advisory-only:
it models sovereign nodes, scoped event exchange, maritime risk, healthcare logistics
visibility, tabletop simulation, governance audit logs, and a TypeScript AetherOS
dashboard without centralizing authority or issuing operational commands.

Key directories:

- `core/` contains shared contracts for jurisdiction scope, recommendations, audit
  metadata, and constraint impacts.
- `federation/` defines sovereign nodes, regional clusters, scoped event bus behavior,
  and audit relay indexing.
- `risk-engine/` contains the inspectable weighted constraint graph and resilience
  scoring model.
- `maritime/` provides conceptual vessel-flow and congestion forecasting utilities.
- `healthcare-logistics/` provides aggregate-only supply stress scoring.
- `simulation/` contains tabletop scenario execution for synthetic disruptions.
- `audit/` and `auth/` provide recommendation replay, explainability, and scoped access
  decisions.
- `dashboard/` contains a React/TypeScript AetherOS dashboard scaffold with modular
  widgets and typed streaming placeholders.
- `docs/architecture/overview.md` describes the federated node model, dashboard layer,
  simulation engine, and governance/audit layer.

## Heritage Stack™ Governance Kernel

The repository now includes a `heritage_stack/` governance layer for Zero-Damage
Mandate and Human-in-the-Loop enforcement. It evaluates proposed actions before any
high-stakes, destructive, external-facing, or system-state-transition workflow can
proceed.

- `ZeroDamageMandate` blocks requests that bypass human authority, hide objectives,
  merge protected datasets, centralize sovereign authority, or issue binding commands.
- `HumanApprovalGate` requires explicit human approval evidence for gated actions.
- `WatchdogDaemon` requires signature quorum evidence for critical system calls; the
  included SHA-256 verifier is deterministic test scaffolding, while production should
  bind the same interface to hardware-backed Ed25519 verification.
- `ZYXKernel` emits inspectable governance decisions and never executes actions itself.

## FMVL NASA ESTO / ESDS Technical Interface Specification

The repository now includes a submission-grade FMVL specification for NASA ESTO / ESDS
SBIR Phase I review contexts. FMVL is a read-only advisory Earth observation layer that
models disagreement between independently produced observation products rather than
resolving truth or controlling any sensing/operational system.

- `docs/fmvl/openapi.json` is the primary OpenAPI 3.0.3 artifact and defines ingest,
  disagreement-field, trust-map, lineage-trace, and advisory-interpretation endpoints.
- `docs/fmvl/technical_specification.md` contains the supporting data model, ESDS-style
  event stream architecture, security/governance model, TRL justification, NASA alignment,
  and comparative prior-art analysis.
- Tests in `tests/test_fmvl_spec.py` verify endpoint coverage, advisory-only semantics,
  security declarations, rate-limit metadata, and required specification sections.

## AetherOS API Emulation + AnnabanOS Integration

The repository now includes a local AetherOS API emulator for deterministic integration
validation. It routes scoped advisory requests to AnnabanOS dry-run execution evaluation
and AnnabanAI fallback automation without exposing command/control pathways.

- `aetheros/` defines the in-process API emulator, versioned route contracts, scoped
  modes, capability ceilings, and normalized advisory responses.
- `annabanos/` defines dry-run execution requests and results, evaluates proposed actions
  through the Heritage Stack `ZYXKernel`, and blocks external/high-stakes actions unless
  HITL and Watchdog requirements are satisfied.
- `docs/aetheros/api_emulation.md` documents the emulator routes, governance behavior,
  and integration boundaries.
- `tests/test_aetheros_annabanos.py` validates status routing, governance blocking,
  dry-run planning, fallback AnnabanAI automation, Annaban boot simulation, and simulation-scope enforcement.

### Annaban Boot Simulation

The AetherOS emulator now exposes `/api/v1/annaban/boot-simulation` to simulate Annaban boot from AnnabanAI emulation. The simulation returns a dry-run persona profile, module readiness stages (persona kernel, simulated learning environment, memory buckets, reward generator, and portfolio builder), and an AnnabanAI fallback automation summary. It performs no external actions and persists no private memory bucket data.

### Recent Architecture Hardening

- Added chained audit JSONL records (`previous_hash`, `payload_hash`, `event_hash`) and runtime health reporting for audit-chain verification.
- Added a `MemoryBackend` protocol to isolate runtime persistence from the current SQLite implementation.
- Added versioned AetherOS emulator routes under `/api/v1`.
- Added route capability ceilings (`read_only`, `advisory`, `simulation`, `external_effect`, `critical`) to reject escalation before subsystem delegation.
- Added optional `expires_at` visibility-scope TTLs to prevent stale temporary access windows.
