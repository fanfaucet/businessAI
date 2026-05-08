# FMVL NASA ESTO / ESDS Phase I Technical Interface Specification

## 1. System Architecture Overview

**System name:** Federated Multi-Source Verification Layer (FMVL)  
**Target context:** NASA ESTO / ESDS SBIR Phase I implementation analysis  
**System class:** Read-only Earth observation disagreement quantification and provenance layer

FMVL is an advisory-only Earth science data system component that quantifies disagreement among multiple Earth observation sources. The system does **not** resolve truth, average competing products into a single operational answer, control sensors, task platforms, or issue downstream operational instructions. FMVL models disagreement between independently produced Earth observation assertions and preserves lineage for audit and reproducibility.

Primary functions:

1. Ingest Earth observation metadata and payload references.
2. Compute Consensus Gap Fields (CGFs) that represent structural divergence.
3. Produce trust maps and trust vectors from lineage, calibration, consistency, and anomaly evidence.
4. Maintain hash-chained lineage traces using SHA-256 content and transition hashes.
5. Emit advisory interpretations for human review.
6. Publish ESDS-style events for downstream data-system interoperability.

Primary non-functions:

- No control system design.
- No sensor command, retasking, calibration change, or platform steering interface.
- No closed-loop operational authority.
- No kinetic, military, geopolitical, or emergency-response directive semantics.
- No assertion that CGF output is ground truth.

## 2. OpenAPI 3.0 Primary Artifact

The OpenAPI 3.0.3 artifact is maintained at:

- `docs/fmvl/openapi.json`

It defines the following endpoints:

| Endpoint | Method | Purpose | Advisory boundary |
| --- | --- | --- | --- |
| `/ingest/observation` | `POST` | Register Earth observation metadata and lineage references. | Accepts data only; cannot control sensors. |
| `/analyze/disagreement-field` | `POST` | Compute a Consensus Gap Field from two or more observations. | Models divergence; does not resolve truth. |
| `/metrics/trust-map` | `POST` | Generate trust vectors and trust-map references. | Quality indicator only. |
| `/audit/lineage-trace` | `GET` | Retrieve lineage trace and hash-chain validation state. | Read-only audit lookup. |
| `/advisory/interpretation` | `POST` | Generate advisory interpretation of CGF and trust products. | Non-operational interpretation for human review. |

Versioning strategy:

- API version is declared in `info.version` using semantic versioning with a Phase I suffix.
- Breaking changes require a new major version and parallel deployment window.
- URL-neutral media negotiation is preferred until a major-version break is required.

Conservative Phase I rate limits:

| Operation class | Default limit | Scope |
| --- | ---: | --- |
| Observation ingest | 60 requests/minute | API key or signed-token subject |
| CGF analysis | 20 requests/minute | API key or signed-token subject |
| Trust-map generation | 30 requests/minute | API key or signed-token subject |
| Lineage trace reads | 120 requests/minute | API key or signed-token subject |
| Advisory interpretation | 30 requests/minute | API key or signed-token subject |

Authentication model:

- `X-FMVL-API-Key` for read-only advisory API access.
- Signed bearer token (`JWT` or detached `JWS`) carrying subject, issuer, scope, expiry, and advisory-only claims.
- Tokens must not include sensor-control, tasking, or operational-command scopes.

## 3. Data Model Specification

### 3.1 Observation Schema

| Field | Type | Required | Constraints | Notes |
| --- | --- | --- | --- | --- |
| `observation_id` | string | Yes | 8–128 chars | Stable identifier. |
| `variable` | string | Yes | 2–96 chars | Earth observation variable such as `soil_moisture`. |
| `observed_at` | RFC 3339 date-time | Yes | UTC recommended | Supports time-series indexing. |
| `valid_time_end` | RFC 3339 date-time | No | Must be >= `observed_at` | Supports interval products. |
| `geometry` | GeoJSON Point/Polygon/MultiPolygon | Yes | WGS84 recommended | Spatial search and grid alignment. |
| `value` | number or number array | Yes | Numeric finite values | Scalar, vector, or compact gridded summary. |
| `units` | string | Yes | 1–32 chars | UCUM-compatible units recommended. |
| `uncertainty` | number | No | >= 0 | Native source uncertainty. |
| `spatial_resolution_m` | number | No | > 0 | Spatial compatibility metadata. |
| `temporal_resolution_s` | number | No | > 0 | Time-series compatibility metadata. |
| `quality_flags` | string[] | Yes | Max 32 flags | Source quality annotations. |
| `data_uri` | URI | No | DAAC-compatible pointer preferred | External granule/object reference. |

Time-series compatibility notes:

- `observed_at` is the primary temporal index.
- `valid_time_end` allows interval and composited products.
- FMVL analysis windows must explicitly define `start` and `end` to avoid implicit temporal interpolation.
- Observations with incompatible temporal resolutions should be marked in CGF cells as `temporal_phase` or `insufficient_overlap` disagreements.

### 3.2 Sensor Schema

| Field | Type | Required | Constraints | Notes |
| --- | --- | --- | --- | --- |
| `sensor_id` | string | Yes | 2–128 chars | Instrument/source identifier. |
| `platform` | string | Yes | 2–128 chars | Satellite, airborne platform, station, or model system. |
| `instrument` | string | Yes | 2–128 chars | Instrument or model product name. |
| `source_type` | enum | Yes | `satellite`, `airborne`, `in_situ`, `model_reanalysis`, `derived_product`, `synthetic_validation` | Enables source stratification. |
| `calibration_version` | string | Yes | 1–64 chars | Calibration lineage key. |
| `processing_level` | enum | No | `L0`, `L1`, `L2`, `L3`, `L4`, `model` | ESDS product-level compatibility. |
| `producer` | string | No | <= 128 chars | Producing system or archive. |

### 3.3 Consensus Gap Field (CGF) Schema

CGF represents structural divergence, not consensus truth. Each CGF contains a gridded or cell-indexed disagreement field.

| Field | Type | Required | Constraints | Notes |
| --- | --- | --- | --- | --- |
| `cgf_id` | string | Yes | 8–128 chars | Stable CGF identifier. |
| `variable` | string | Yes | 2–96 chars | Earth observation variable. |
| `analysis_window` | object | Yes | RFC 3339 start/end | Explicit temporal bounds. |
| `spatial_grid` | object | Yes | CRS, resolution, bounds | Analysis grid definition. |
| `gap_statistics` | object | Yes | Non-negative gap values | Summary metrics. |
| `cells` | `CGFCell[]` | Yes | At least 1 | Cell-level divergence. |
| `lineage_id` | string | Yes | 8–128 chars | Audit trace root. |
| `advisory_only` | boolean | Yes | Must be `true` | Safety boundary. |

`CGFCell` includes `gap_magnitude`, `gap_direction`, `source_count`, confidence, and dominant disagreement mode. Dominant modes include bias, variance, spatial gradient, temporal phase, lineage quality, and insufficient overlap.

### 3.4 Trust Vector Schema

Trust vectors are quality and provenance indicators. They do not assign truth.

| Field | Type | Required | Range | Interpretation |
| --- | --- | --- | --- | --- |
| `entity_id` | string | Yes | 8–128 chars | Observation, CGF, or advisory entity. |
| `lineage_score` | number | Yes | 0–1 | Completeness and integrity of provenance. |
| `calibration_score` | number | Yes | 0–1 | Calibration metadata currency. |
| `consistency_score` | number | Yes | 0–1 | Agreement with comparable sources. |
| `anomaly_score` | number | Yes | 0–1 | Higher means stronger anomaly evidence. |
| `aggregate_trust` | number | Yes | 0–1 | Weighted indicator for review prioritization. |

### 3.5 Lineage Trace Schema

Lineage traces are parent-child provenance graphs with hash-chain integrity metadata.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `lineage_id` | string | Yes | Trace identifier. |
| `entity_id` | string | Yes | Entity being traced. |
| `nodes` | `LineageNode[]` | Yes | Observation, sensor, CGF, trust-map, advisory nodes. |
| `edges` | `LineageEdge[]` | Yes | Derivation and comparison relationships. |
| `hash_chain_valid` | boolean | Yes | Result of lineage hash validation. |

Hashing model:

- `content_sha256 = SHA-256(canonical_entity_payload)`.
- `current_hash = SHA-256(previous_hash || content_sha256 || entity_id || created_at)`.
- The first node uses `previous_hash = GENESIS`.
- Hash records are lineage integrity metadata, not distributed-ledger finality.

## 4. Event Stream Architecture (ESDS-Style)

FMVL uses a Kafka-like event abstraction for integration with ESDS-compatible processing pipelines. The specification does not require a specific broker implementation in Phase I.

### 4.1 Topics and Event Types

| Event type | Topic | Producer | Consumer class |
| --- | --- | --- | --- |
| `observation.ingested` | `fmvl.observation` | Ingest service | Lineage logger, CGF scheduler |
| `disagreement.detected` | `fmvl.disagreement` | CGF engine | Trust-map service, advisory service |
| `trust.updated` | `fmvl.trust` | Trust metrics service | Advisory service, dashboards |
| `lineage.logged` | `fmvl.lineage` | Audit service | Audit readers, validation jobs |
| `advisory.emitted` | `fmvl.advisory` | Advisory service | Human review dashboards |

### 4.2 Event Envelope

```json
{
  "event_id": "evt-2026-00000001",
  "event_type": "disagreement.detected",
  "occurred_at": "2026-05-07T00:00:00Z",
  "producer": "fmvl-cgf-engine",
  "schema_version": "0.1.0",
  "correlation_id": "corr-abc12345",
  "entity_id": "cgf-abc12345",
  "advisory_only": true,
  "payload_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "payload": {
    "cgf_id": "cgf-abc12345",
    "variable": "soil_moisture",
    "mean_gap": 0.18,
    "max_gap": 0.42,
    "coverage_fraction": 0.91
  }
}
```

### 4.3 Ordering Guarantees

- Per-entity ordering is required by `entity_id` partition key.
- Cross-entity global ordering is not assumed.
- Consumers must tolerate eventual consistency across observations, CGFs, trust maps, and advisory products.
- Replay must be deterministic for a fixed event log, schema version, and analysis configuration.

### 4.4 Replay Semantics

- Event retention target for Phase I validation: 30 days minimum in the reference environment.
- Replay consumers must start from a recorded offset and validate `payload_sha256` before processing.
- Lineage replay must reconstruct parent-child edges and verify each hash-chain transition.
- Replayed advisory outputs must remain advisory-only and be marked as replay products.

### 4.5 Failure Handling

- Schema validation failure: route to `fmvl.deadletter.schema` with original event hash and validation error.
- Hash validation failure: route to `fmvl.deadletter.integrity` and mark entity trust vector with elevated anomaly score.
- Late observation arrival: emit compensating `trust.updated` and, if necessary, new `disagreement.detected`; do not overwrite immutable prior CGF records.
- Duplicate observation: return HTTP `409` or emit idempotent duplicate notice with original lineage id.

## 5. Security and Governance Model

### 5.1 Read-Only Enforcement Model

FMVL exposes no interface for sensor retasking, instrument configuration, actuator access, platform steering, operational scheduling, or downstream system actuation. All endpoints carry `x-advisory-only: true`, and the OpenAPI operation set contains no command/control path.

Allowed verbs:

- Ingest observation metadata.
- Analyze disagreement.
- Retrieve metrics.
- Retrieve lineage.
- Generate advisory interpretation.

Disallowed interface categories:

- Sensor control.
- Platform tasking.
- Operational routing.
- Closed-loop response automation.
- Any endpoint that claims authority to determine ground truth.

### 5.2 Anti-Command Constraint Layer

The advisory service must reject output text containing directive operational language. Required output constraints:

- State uncertainty and limitations.
- State that CGF does not resolve truth.
- Use review-oriented phrasing such as "indicates", "suggests", "requires data steward review".
- Avoid operational imperatives such as "execute", "retask", "reroute", "deploy", or "activate".

### 5.3 Lineage Integrity Hashing Model

FMVL uses canonical JSON serialization and SHA-256 hashes for lineage integrity:

1. Canonicalize entity payload with stable key ordering.
2. Compute content hash.
3. Combine previous hash, content hash, entity id, and timestamp.
4. Store current hash in immutable lineage record.
5. Validate chain transitions during audit retrieval and replay.

This is a provenance integrity mechanism, not a distributed ledger.

### 5.4 Sensor Spoofing Mitigation Strategy

Phase I mitigation controls:

- Require sensor identity metadata and calibration version.
- Compare observed spatiotemporal footprint against declared platform/source type.
- Track producer and processing-level consistency.
- Elevate anomaly score when lineage gaps or impossible temporal/spatial jumps appear.
- Cross-check value ranges and gradients against comparable sources without averaging them into truth.

### 5.5 Adversarial Injection Detection Model

Detection features:

- Duplicate content hash with conflicting metadata.
- Rapid source identity churn.
- Unusual value distribution relative to source-specific historical envelope.
- Lineage discontinuity or invalid parent references.
- CGF cells dominated by a single low-lineage source.

Response model:

- Mark affected trust vectors with elevated anomaly score.
- Emit `trust.updated` and `lineage.logged` events.
- Preserve original records for audit.
- Do not delete, alter, or operationally suppress observations through FMVL APIs.

## 6. TRL Justification

| Subsystem | Phase I target TRL | Justification | Synthetic validation assumptions |
| --- | ---: | --- | --- |
| OpenAPI interface layer | TRL 4 | Interface can be validated in a laboratory environment with schema tests and mock services. | Synthetic observation payloads and mock auth tokens. |
| Observation ingest + validation | TRL 4 | Core metadata validation and lineage registration can be demonstrated with representative EO metadata. | No live DAAC production integration assumed. |
| CGF engine | TRL 3–4 | Mathematical formulation and proof-of-concept divergence metrics can be demonstrated, but operational validity requires broader dataset evaluation. | Synthetic multi-source disagreement cases plus small public sample datasets in later work. |
| Trust-map metrics | TRL 3 | Trust vector logic is analytical and requires calibration against curated provenance-quality examples. | Synthetic lineage completeness and anomaly scenarios. |
| Hash-chained lineage audit | TRL 4–5 | Deterministic content hashing and replay validation are established engineering patterns. | Laboratory object store or file-backed audit records. |
| Event stream integration | TRL 4 | Kafka-like broker semantics can be validated with local containers or managed test topics. | No production ESDS event bus dependency in Phase I. |
| Advisory interpretation | TRL 3 | Output framing constraints and templates can be validated; scientific usefulness requires user evaluation. | Template-based outputs from synthetic CGF/trust-map inputs. |
| Security and anti-command layer | TRL 3–4 | Static constraints and auth scopes can be validated, but adversarial robustness requires red-team testing. | Synthetic spoofing and injection cases. |

Maturity is intentionally not inflated. Phase I establishes feasibility, interface rigor, and laboratory validation evidence. Production ESDS integration and operational science assessment remain later-phase work.

## 7. NASA ESTO / ESDS Alignment

### 7.1 NASA Earth Science Data Systems (ESDS)

FMVL aligns with ESDS priorities by defining interoperable APIs, provenance-first data products, reproducible analysis windows, and event-driven integration boundaries. The system is an analysis and metadata layer, not a control layer.

### 7.2 DAAC Interoperability Principles

DAAC compatibility considerations:

- `data_uri` fields can reference archive-managed granules or derived products.
- Lineage records preserve producer, processing step, and parent entity identifiers.
- OpenAPI schemas use strict typing and stable identifiers for integration validation.
- Event replay supports reproducibility and downstream indexing.

### 7.3 Earth Observation Uncertainty Quantification

FMVL contributes to uncertainty quantification by modeling structural disagreement among sources. CGF outputs identify where source products diverge by magnitude, direction, mode, and confidence. This differs from uncertainty reduction; the output is an explicit disagreement representation.

### 7.4 FAIR Data and Provenance

- Findable: stable identifiers for observations, CGFs, trust maps, and advisory records.
- Accessible: documented HTTP API and event schemas.
- Interoperable: JSON/OpenAPI schemas, GeoJSON-compatible geometry, RFC 3339 time.
- Reusable: lineage traces, hash integrity, and explicit limitations.

## 8. Comparative Prior Art

### 8.1 Bayesian Model Averaging

Bayesian Model Averaging combines model outputs by posterior model probabilities to produce weighted estimates. FMVL does not produce a fused estimate and does not assign posterior truth. CGF instead preserves divergence structure as a first-class product.

### 8.2 Kalman Filter / Ensemble Kalman Methods

Kalman and Ensemble Kalman methods update state estimates using observation and model covariance assumptions. FMVL is not a state estimator. It does not assimilate observations into a control or forecast state; it quantifies disagreement among independently generated Earth observation assertions.

### 8.3 Dempster-Shafer Evidence Theory

Dempster-Shafer methods combine belief masses under defined frames of discernment. FMVL does not combine evidence into belief intervals. It creates spatial-temporal disagreement fields, trust vectors, and lineage traces to expose divergence and provenance quality.

### 8.4 Standard Multi-Sensor Fusion Pipelines

Standard fusion pipelines often harmonize, resample, weight, and merge sources into a single product. FMVL is structurally different: it treats disagreement as the output rather than an error to remove. CGF is a divergence product, not an improved fused observation.

## 9. Implementation Notes

Recommended Phase I implementation sequence:

1. Validate OpenAPI schemas and advisory-only extensions.
2. Implement mock service endpoints with deterministic synthetic fixtures.
3. Implement lineage canonicalization and SHA-256 transition hashing.
4. Implement baseline CGF metrics: distributional distance and lineage-weighted residual.
5. Implement event envelope publisher with local broker abstraction.
6. Implement advisory text constraints and output validation.
7. Execute synthetic validation suite with sensor spoofing and lineage discontinuity cases.

Reviewer-facing validation artifacts:

- OpenAPI schema validation output.
- Synthetic ingest/analyze/trust/audit/advisory transaction logs.
- Lineage hash-chain replay report.
- CGF reproducibility notebook or script.
- Advisory-only output constraint test results.
