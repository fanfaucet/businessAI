"""Watchdog Daemon signature-quorum validation."""

from __future__ import annotations

import hashlib

from heritage_stack.models import ActionRequest, SignatureEnvelope


class DeterministicSha256Verifier:
    """Offline verifier for deterministic tests and air-gapped scaffolding.

    This is not a production Ed25519 implementation. It verifies that signatures
    match a deterministic SHA-256 digest formed from key id and message digest.
    Production systems should replace this with hardware-backed Ed25519 checks.
    """

    algorithm = "sha256-test"

    def sign(self, key_id: str, message_sha256: str) -> str:
        return hashlib.sha256(f"{key_id}:{message_sha256}".encode("utf-8")).hexdigest()

    def verify(self, envelope: SignatureEnvelope) -> bool:
        if envelope.algorithm != self.algorithm:
            return False
        expected = self.sign(envelope.key_id, envelope.message_sha256)
        return envelope.signature == expected


class WatchdogDaemon:
    """Validate cryptographic integrity requirements before critical actions."""

    def __init__(self, required_signatures: int = 2, verifier: DeterministicSha256Verifier | None = None) -> None:
        if required_signatures < 1:
            raise ValueError("At least one signature is required")
        self.required_signatures = required_signatures
        self.verifier = verifier or DeterministicSha256Verifier()

    def message_sha256(self, request: ActionRequest) -> str:
        material = "|".join(
            [
                request.request_id,
                request.title,
                request.description,
                request.category.value,
                request.actor_id,
                request.target,
                request.jurisdiction_id,
            ]
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def validate(self, request: ActionRequest, signatures: list[SignatureEnvelope]) -> tuple[bool, list[str], int]:
        expected_digest = self.message_sha256(request)
        valid_signers = set()
        findings: list[str] = []
        for envelope in signatures:
            if envelope.message_sha256 != expected_digest:
                findings.append(f"Signature from {envelope.signer_id} targets a different message digest")
                continue
            if not self.verifier.verify(envelope):
                findings.append(f"Signature from {envelope.signer_id} failed verification")
                continue
            valid_signers.add(envelope.signer_id)
        if len(valid_signers) < self.required_signatures:
            findings.append("Signature quorum not satisfied")
        return len(valid_signers) >= self.required_signatures, findings, len(valid_signers)
