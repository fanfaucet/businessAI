"""Inspectable role and scope checks for zero-trust access decisions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.contracts import JurisdictionScope, VisibilityScope


class Role(str, Enum):
    SOVEREIGN_OPERATOR = "sovereign_operator"
    COALITION_ANALYST = "coalition_analyst"
    EMERGENCY_COORDINATOR = "emergency_coordinator"
    SIMULATION_USER = "simulation_user"
    AUDITOR = "auditor"


@dataclass(frozen=True)
class Principal:
    principal_id: str
    roles: tuple[Role, ...]
    jurisdiction_id: str
    key_ref: str


def can_view(principal: Principal, scope: JurisdictionScope) -> bool:
    if Role.AUDITOR in principal.roles:
        return True
    if scope.visibility == VisibilityScope.SIMULATION_ONLY:
        return Role.SIMULATION_USER in principal.roles or Role.SOVEREIGN_OPERATOR in principal.roles
    if scope.visibility == VisibilityScope.SOVEREIGN:
        return Role.SOVEREIGN_OPERATOR in principal.roles and principal.jurisdiction_id == scope.jurisdiction_id
    if scope.visibility == VisibilityScope.COALITION:
        return Role.COALITION_ANALYST in principal.roles or principal.jurisdiction_id == scope.jurisdiction_id
    if scope.visibility == VisibilityScope.EMERGENCY:
        return Role.EMERGENCY_COORDINATOR in principal.roles or principal.jurisdiction_id == scope.jurisdiction_id
    return False
