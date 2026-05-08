# Federation

Purpose: sovereign node and regional-cluster topology definitions.

Architecture: federation uses autonomous sovereign nodes, regional clusters, and audit relays. Nodes exchange scoped events with eventual consistency; they do not delegate authority to a central orchestrator.

Interfaces: see `node_model.py` for node, cluster, event bus, and audit relay contracts.
