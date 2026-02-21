from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import DnsTxtRecord


@dataclass
class NamecheapCredentials:
    """Credentials required for Namecheap API access."""

    api_user: str
    api_key: str
    username: str
    client_ip: str


class NamecheapDnsPlanner:
    """Pure planning layer for deterministic DNS updates.

    This class deliberately does not make HTTP requests yet.
    It computes the desired record set so the transport layer
    can safely apply it during OAuth-backed automation.
    """

    @staticmethod
    def merge_records(existing: Iterable[DnsTxtRecord], target: DnsTxtRecord) -> list[DnsTxtRecord]:
        """Replace conflicting _atproto record while preserving unrelated records."""

        merged = [record for record in existing if record.host != target.host]
        merged.append(target)
        return merged
