from __future__ import annotations

from dataclasses import dataclass

from .models import DnsTxtRecord, DomainVerificationRequest, Registrar
from .namecheap import NamecheapDnsPlanner


@dataclass(frozen=True)
class DomainPlan:
    """Deterministic plan produced before touching registrar APIs."""

    request: DomainVerificationRequest
    records_before: tuple[DnsTxtRecord, ...]
    records_after: tuple[DnsTxtRecord, ...]
    actions: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        """Serialize plan into API-friendly primitives for preview mode."""

        return {
            "domain": self.request.domain,
            "did": self.request.did,
            "registrar": self.request.registrar.value,
            "records_before": [record.__dict__ for record in self.records_before],
            "records_after": [record.__dict__ for record in self.records_after],
            "actions": list(self.actions),
        }


class DomainAgent:
    """Application-facing orchestration layer for domain verification planning."""

    def build_plan(
        self,
        request: DomainVerificationRequest,
        existing_records: list[DnsTxtRecord],
    ) -> DomainPlan:
        if request.registrar != Registrar.NAMECHEAP:
            raise ValueError(f"Unsupported registrar: {request.registrar}")

        merged = NamecheapDnsPlanner.merge_records(existing_records, request.atproto_record)
        actions = self._describe_actions(existing_records, request.atproto_record)
        return DomainPlan(
            request=request,
            records_before=tuple(existing_records),
            records_after=tuple(merged),
            actions=actions,
        )

    def _describe_actions(
        self,
        existing_records: list[DnsTxtRecord],
        target_record: DnsTxtRecord,
    ) -> tuple[str, ...]:
        has_existing = any(record.host == target_record.host for record in existing_records)
        if has_existing:
            return (
                f"remove conflicting {target_record.host} TXT records",
                f"upsert {target_record.host} TXT -> {target_record.value} (ttl={target_record.ttl})",
            )
        return (f"create {target_record.host} TXT -> {target_record.value} (ttl={target_record.ttl})",)
