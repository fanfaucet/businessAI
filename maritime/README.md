# Maritime Logistics

Purpose: advisory maritime logistics analytics for vessel flow, congestion, perturbation, weather disruption, and customs friction.

Architecture: deterministic estimators accept AIS-like positions, weather overlays, trade manifests, and synthetic port telemetry. Outputs are probabilistic risk maps and advisory rerouting suggestions with confidence intervals.

Security: manifests and port telemetry must be scoped before aggregation; no protected data is merged across jurisdictions.
