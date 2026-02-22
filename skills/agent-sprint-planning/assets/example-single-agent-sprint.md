# Sprint Plan: API Key Rotation and Revocation

## 1. Sprint Objective
- Goal: Ship secure API key rotation and revocation for service accounts with audit traceability.
- In scope: Backend endpoints, key hashing/storage updates, policy checks, audit events, automated tests.
- Out of scope: UI management console and customer notification workflows.
- Hard constraints: No plaintext key storage; no breaking change to existing auth middleware.
- Execution mode: `single-agent` | `multi-agent`

## 2. Environment & Gates
- Branch/worktree strategy: One feature branch, linear packet execution.
- Required checks:
  - Build: `npm run build`
  - Tests: `npm test -- api-keys`
  - Lint/type: `npm run lint && npm run typecheck`
  - Security/perf (if applicable): `npm run test:security -- api-keys`

## 3. Packet Backlog
| Packet ID | Title | Scope (files/modules) | Depends On | Parallel Lane | Risk | Status |
|---|---|---|---|---|---|---|
| P1 | Data model + migration for key metadata | `db/migrations/*`, `src/db/apiKeysRepo.ts` | none | lane-1 | high | todo |
| P2 | Rotation service logic | `src/services/apiKeyRotationService.ts` | P1 | lane-1 | medium | todo |
| P3 | Revocation endpoint + auth checks | `src/routes/apiKeys.ts`, `src/middleware/authz.ts` | P2 | lane-1 | high | todo |
| P4 | Audit log emission and schema assertions | `src/services/audit.ts`, `tests/audit/*` | P3 | lane-1 | medium | todo |
| P5 | Integration tests and docs updates | `tests/integration/api-keys/*`, `docs/api-keys.md` | P4 | lane-1 | low | todo |

Status values: `todo`, `in_progress`, `blocked`, `done`.

For `multi-agent` mode, add owner initials and planned handoff point in each packet title or notes.

## 4. Dependency Notes
- Critical path: P1 -> P2 -> P3 -> P4 -> P5
- Explicit blockers: P2 blocked by migration contract in P1; P3 blocked by rotation behavior in P2.
- Safe parallel sets: none (tight coupling and shared contracts).

## 5. Stop-and-Ask Gates
- Gate 1: Migration changes that rewrite historical key data.
- Gate 2: Any authz rule change affecting non-service-account callers.
- Gate 3: Any change requiring plaintext key re-display behavior.

## 6. Re-Planning Policy
- Trigger for split/re-scope: Packet touches more than 8 files or fails verification twice.
- Trigger for escalation: Security test failure or unexpected authz regression.
- Max retries per packet before re-plan: 2

## 7. First Execution Order
1. P1 Data model + migration for key metadata
2. P2 Rotation service logic
3. P3 Revocation endpoint + auth checks

## 8. Multi-Agent Coordination (only if mode is `multi-agent`)
- Lane owners: N/A
- Integration checkpoints: N/A
- Conflict resolution rule (when two lanes touch same files): N/A

---

# Task Card: P2 - Rotation Service Logic

## Objective
- Outcome: Rotate an API key atomically, revoke old key, return one-time cleartext only at creation.
- Why now: P3 revocation endpoint depends on a consistent key state model.
- Mode context: `single-agent` | `multi-agent`

## Scope
- Included files/modules: `src/services/apiKeyRotationService.ts`, `src/db/apiKeysRepo.ts`, `tests/services/apiKeyRotationService.test.ts`
- Excluded files/modules: `src/routes/*`, frontend files, billing services
- Interface/contracts touched: `rotateApiKey(serviceAccountId)` service contract

## Implementation Notes
- Primary approach: transaction-based rotate + revoke flow with optimistic lock on active key row.
- Fallback approach: explicit DB lock per service account keyset.

## Acceptance Criteria
1. Rotation creates exactly one active key and marks prior key revoked.
2. Repeating rotation does not leave multiple active keys.
3. Revoked keys fail auth checks in downstream middleware tests.

## Verification Commands
```bash
npm test -- apiKeyRotationService
npm test -- auth-middleware api-keys
```

## Artifacts Required
- Code changes: rotation service + repository update
- Tests: service unit tests for atomicity and duplicate rotations
- Docs/changelog: `docs/api-keys.md` update for rotation semantics
- Migration/ops notes (if applicable): note on index for active-key uniqueness

## Risk & Rollback
- Risk level: medium | high
- Failure mode: partial rotation leaves ambiguous active key state.
- Rollback/mitigation: disable rotate endpoint via feature flag and restore previous service behavior.

## Dependencies
- Blocks: P3
- Blocked by: P1
- Parallel-safe with: none

## Ownership & Handoff (required for `multi-agent`)
- Owner: single-agent
- Handoff target: same agent
- Handoff contract (what must be true before handoff): N/A

## Stop-and-Ask Triggers
- Trigger 1: transaction semantics differ across deployed DB engines.
- Trigger 2: need to alter existing auth token claims.
