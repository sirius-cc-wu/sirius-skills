# Sprint Plan: API Key Rotation and Revocation

## 1. Sprint Objective
- Goal: Ship secure API key rotation and revocation for service accounts with audit traceability.
- In scope: Backend endpoints, key hashing/storage updates, policy checks, audit events, automated tests.
- Out of scope: UI management console and customer notification workflows.
- Hard constraints: No plaintext key storage; no breaking change to existing auth middleware.
- Execution mode: `single-agent` | `multi-agent`

## 2. Environment & Gates
- Branch/worktree strategy: One integration branch plus one worktree per lane owner.
- Required checks:
  - Build: `npm run build`
  - Tests: `npm test -- api-keys`
  - Lint/type: `npm run lint && npm run typecheck`
  - Security/perf (if applicable): `npm run test:security -- api-keys`

## 3. Packet Backlog
| Packet ID | Title | Scope (files/modules) | Depends On | Parallel Lane | Risk | Status |
|---|---|---|---|---|---|---|
| P1-A (AD) Migration + repo contract | `db/migrations/*`, `src/db/apiKeysRepo.ts` | none | lane-data | high | todo |
| P1-B (SE) Rotation/revocation service | `src/services/apiKeyRotationService.ts` | P1-A | lane-service | medium | todo |
| P1-C (BE) Route + authz policy enforcement | `src/routes/apiKeys.ts`, `src/middleware/authz.ts` | P1-B | lane-api | high | todo |
| P2-A (QA) Integration tests matrix | `tests/integration/api-keys/*` | P1-C | lane-quality | medium | todo |
| P2-B (DX) Docs + changelog + rollout notes | `docs/api-keys.md`, `CHANGELOG.md` | P1-C | lane-docs | low | todo |
| P3 (INT) Cross-lane merge and final verification | integration branch | P2-A, P2-B | lane-integration | high | todo |

Status values: `todo`, `in_progress`, `blocked`, `done`.

For `multi-agent` mode, add owner initials and planned handoff point in each packet title or notes.

## 4. Dependency Notes
- Critical path: P1-A -> P1-B -> P1-C -> P2-A/P2-B -> P3
- Explicit blockers: API lane blocked by service contract lock; quality/docs lanes blocked by endpoint behavior freeze.
- Safe parallel sets: P2-A and P2-B can run in parallel after P1-C.

## 5. Stop-and-Ask Gates
- Gate 1: Migration operation beyond additive schema/index changes.
- Gate 2: Authz policy broadening for any non-service-account path.
- Gate 3: Integration conflicts touching `src/middleware/authz.ts` and `src/routes/apiKeys.ts` simultaneously.

## 6. Re-Planning Policy
- Trigger for split/re-scope: Any lane blocked > 30 minutes or packet exceeds 8 files.
- Trigger for escalation: Merge conflict on shared contracts or failing security gate.
- Max retries per packet before re-plan: 2

## 7. First Execution Order
1. P1-A (AD) Migration + repo contract
2. P1-B (SE) Rotation/revocation service
3. P1-C (BE) Route + authz policy enforcement

## 8. Multi-Agent Coordination (only if mode is `multi-agent`)
- Lane owners: AD=data, SE=service, BE=backend API, QA=quality, DX=docs, INT=integration
- Integration checkpoints:
  - Checkpoint 1: Contract freeze after P1-B
  - Checkpoint 2: Endpoint behavior freeze after P1-C
  - Checkpoint 3: Full gate run in P3
- Conflict resolution rule (when two lanes touch same files): contract owner (upstream lane) decides, INT lane records final merge note.

---

# Task Card: P2-A - Integration Tests Matrix

## Objective
- Outcome: Verify rotate/revoke behaviors across success, repeat, and unauthorized scenarios.
- Why now: Multi-lane work requires a shared, deterministic integration quality gate.
- Mode context: `single-agent` | `multi-agent`

## Scope
- Included files/modules: `tests/integration/api-keys/rotation.test.ts`, `tests/integration/api-keys/revocation.test.ts`
- Excluded files/modules: migration scripts, route implementation files
- Interface/contracts touched: API contract at `POST /service-accounts/:id/keys/rotate` and `POST /service-accounts/:id/keys/revoke`

## Implementation Notes
- Primary approach: table-driven integration cases for role and key-state permutations.
- Fallback approach: split scenarios into separate suites if setup contention appears.

## Acceptance Criteria
1. Unauthorized caller matrix consistently returns policy denial.
2. Repeat rotation/revocation cases are idempotent by contract.
3. Audit event assertions pass for every mutation action.

## Verification Commands
```bash
npm test -- tests/integration/api-keys/rotation.test.ts
npm test -- tests/integration/api-keys/revocation.test.ts
```

## Artifacts Required
- Code changes: new integration test suites
- Tests: rotate/revoke full matrix
- Docs/changelog: add API behavior examples referenced by docs lane
- Migration/ops notes (if applicable): none

## Risk & Rollback
- Risk level: medium
- Failure mode: flaky setup leads to false negatives and lane blocking.
- Rollback/mitigation: isolate DB fixtures per suite and re-run via deterministic seed.

## Dependencies
- Blocks: P3
- Blocked by: P1-C
- Parallel-safe with: P2-B

## Ownership & Handoff (required for `multi-agent`)
- Owner: QA
- Handoff target: INT
- Handoff contract (what must be true before handoff): both suites green and fixtures documented in test README.

## Stop-and-Ask Triggers
- Trigger 1: observed contract mismatch between route response and agreed schema.
- Trigger 2: integration runtime exceeds CI budget threshold.
