# Core

Purpose: shared contracts for AnnabanAI, AetherOS, and AnnabanOS.

Architecture: this layer defines advisory recommendations, sovereign scopes, audit metadata, constraints, and event envelopes used by all subsystems. It intentionally contains no centralized command logic.

Security: every structure carries jurisdiction/scope fields so protected data can remain segmented.
