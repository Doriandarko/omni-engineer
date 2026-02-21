from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Registrar(str, Enum):
    """Supported DNS providers for sovereign-handle onboarding."""

    NAMECHEAP = "namecheap"


@dataclass(frozen=True)
class DnsTxtRecord:
    """Canonical representation of an _atproto TXT record."""

    host: str
    value: str
    ttl: int = 60


@dataclass(frozen=True)
class DomainVerificationRequest:
    """Data required to anchor a DID to a user-owned domain."""

    domain: str
    did: str
    registrar: Registrar = Registrar.NAMECHEAP

    @property
    def atproto_record(self) -> DnsTxtRecord:
        return DnsTxtRecord(host="_atproto", value=f"did={self.did}")
