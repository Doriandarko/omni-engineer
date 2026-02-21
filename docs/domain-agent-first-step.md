# DomainAgent First Step: Ship the Registrar Contract Vertical Slice

To bring the onboarding agent to life, the first step is to lock down the **registrar contract** as an executable vertical slice (mocked transport, real orchestration).

## First step (what we do now)

Build and expose one end-to-end flow that is safe by default:

1. Accept a `domain + did:plc` onboarding request.
2. Compute the target `_atproto` TXT record (`did=did:plc:...`).
3. Merge against existing records and remove conflicting `_atproto` values.
4. Return a reviewable before/after plan and a machine-readable list of actions.
5. Keep registrar writes disabled behind a transport interface until OAuth is connected.

This gives the UI and agent a stable API immediately while eliminating accidental DNS mutations during early rollout.

## Day-1 execution plan (ship this before OAuth UI)

1. Define the request/response contract for `DomainAgent.build_plan` as the onboarding system boundary.
2. Keep the planner transport-agnostic and pure (no live Namecheap writes).
3. Return deterministic `records_before`, `records_after`, and action metadata so the frontend can render a review screen.
4. Add contract tests that prove:
   - conflicting `_atproto` records are replaced,
   - unrelated DNS records are preserved,
   - unsupported registrars fail fast.
5. Expose this flow via the onboarding API as a **preview mode** endpoint.

If this preview contract is stable, every subsequent piece (OAuth, DNS write transport, verification polling, and AT verification callback) can be integrated in parallel.

## Why this is the highest-leverage first move

- It creates a single source of truth for DNS intent before automation touches production records.
- It unblocks parallel work:
  - OAuth UI can be built against the contract now.
  - Namecheap transport can be implemented behind the same interface.
  - Verification polling can consume the same plan output.
- It keeps risk low: deterministic planning is testable, observable, and reversible.

## Definition of done for Step 1

- Deterministic planner behavior is covered by unit tests.
- A `DomainAgent` orchestration seam returns `records_before` and `records_after`.
- Unsupported registrars fail fast with clear errors.
- API-facing docs describe the request/response contract for the onboarding UI.

## Immediate follow-up sequence

1. **OAuth integration:** connect Namecheap with DNS-scope permissions only.
2. **Transport implementation:** map planner output to `domains.dns.setHosts` payloads.
3. **Verification loop:** poll public resolvers every 30 seconds until `_atproto` matches.
4. **Completion action:** call AT Protocol DNS verification and return success state to the user.

---

If we execute only one thing first, execute this contract slice. Every later feature in the Sovereign Gateway depends on it.

### Preview response shape (contract v1)

`DomainAgent.build_plan` should return:

- `records_before`: tuple of existing DNS records
- `records_after`: tuple with `_atproto` reconciled
- `actions`: ordered, machine-readable action list for UI review
- `to_dict()`: API-safe payload for onboarding preview mode

This keeps the first step deterministic and immediately consumable by an OAuth UI and backend preview endpoint.
