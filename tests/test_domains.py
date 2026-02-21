from forge.domains import DomainAgent, DnsTxtRecord, DomainVerificationRequest, NamecheapDnsPlanner
from forge.domains.models import Registrar


def test_domain_request_builds_atproto_record():
    request = DomainVerificationRequest(domain="privateclient.ai", did="did:plc:abc123")

    assert request.atproto_record == DnsTxtRecord(host="_atproto", value="did=did:plc:abc123", ttl=60)


def test_namecheap_planner_replaces_conflicting_atproto_record():
    existing = [
        DnsTxtRecord(host="@", value="example"),
        DnsTxtRecord(host="_atproto", value="did=did:plc:old"),
    ]
    target = DnsTxtRecord(host="_atproto", value="did=did:plc:new")

    merged = NamecheapDnsPlanner.merge_records(existing, target)

    assert DnsTxtRecord(host="@", value="example") in merged
    assert DnsTxtRecord(host="_atproto", value="did=did:plc:new") in merged
    assert DnsTxtRecord(host="_atproto", value="did=did:plc:old") not in merged


def test_domain_agent_builds_deterministic_plan():
    request = DomainVerificationRequest(domain="privateclient.ai", did="did:plc:new")
    existing = [
        DnsTxtRecord(host="@", value="keep"),
        DnsTxtRecord(host="_atproto", value="did=did:plc:old"),
    ]

    plan = DomainAgent().build_plan(request, existing)

    assert plan.request == request
    assert plan.records_before == tuple(existing)
    assert plan.records_after == (
        DnsTxtRecord(host="@", value="keep"),
        DnsTxtRecord(host="_atproto", value="did=did:plc:new", ttl=60),
    )
    assert plan.actions == (
        "remove conflicting _atproto TXT records",
        "upsert _atproto TXT -> did=did:plc:new (ttl=60)",
    )


def test_domain_agent_create_action_when_record_absent():
    request = DomainVerificationRequest(domain="privateclient.ai", did="did:plc:new")

    plan = DomainAgent().build_plan(request, [DnsTxtRecord(host="@", value="keep")])

    assert plan.actions == ("create _atproto TXT -> did=did:plc:new (ttl=60)",)


def test_domain_plan_to_dict_contains_preview_payload():
    request = DomainVerificationRequest(domain="privateclient.ai", did="did:plc:new")
    plan = DomainAgent().build_plan(request, [DnsTxtRecord(host="@", value="keep")])

    assert plan.to_dict() == {
        "domain": "privateclient.ai",
        "did": "did:plc:new",
        "registrar": Registrar.NAMECHEAP.value,
        "records_before": [{"host": "@", "value": "keep", "ttl": 60}],
        "records_after": [
            {"host": "@", "value": "keep", "ttl": 60},
            {"host": "_atproto", "value": "did=did:plc:new", "ttl": 60},
        ],
        "actions": ["create _atproto TXT -> did=did:plc:new (ttl=60)"],
    }


def test_domain_agent_rejects_unknown_registrar():
    request = DomainVerificationRequest(
        domain="privateclient.ai",
        did="did:plc:new",
        registrar="other",  # type: ignore[arg-type]
    )

    try:
        DomainAgent().build_plan(request, [])
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Unsupported registrar" in str(exc)
