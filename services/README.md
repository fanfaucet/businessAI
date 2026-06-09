# Services

Purpose: event-driven microservice boundaries for federated intelligence services.

Architecture: services should consume scoped events, produce advisory recommendations, and write audit records. They should not become a centralized control plane.

Interfaces: see `interfaces.proto` for gRPC-style service contracts. These are conceptual schemas and are not generated in this repository yet.
