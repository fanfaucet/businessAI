# Gateways

Purpose: ingress/egress boundaries for AIS-like feeds, weather overlays, manifests, telemetry, and dashboard streams.

Architecture: gateways validate scope, redact protected fields, sign events, and publish to sovereign event buses. They should not perform hidden optimization.
