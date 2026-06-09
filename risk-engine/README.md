# Risk Engine

Purpose: compute explainable risk and resilience signals from segmented infrastructure constraints.

Architecture: the engine uses weighted graph relationships to model autonomy, infrastructure load, healthcare stress, performance, and geopolitical friction. It produces advisory load-balancing recommendations only; it does not command operations.

Security: inputs should be pre-scoped by jurisdiction. Cross-jurisdiction graph sharing should use aggregated constraint summaries rather than raw protected data.
