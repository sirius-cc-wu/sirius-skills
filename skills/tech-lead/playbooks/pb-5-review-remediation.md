# Playbook 5: Review Remediation (Gate 2 & PR Findings)

**Trigger:** Unresolved PR comments, Gate 2 review findings, or security audit issues.
**Alpha Progression:** *Work* → *Concluded (Targeted)*.

## Steps

1. **Review Intake & Audit**
   - Run multi-axis review using `code-review-and-quality` or `review-pr`, or ingest Gate 2 reviewer findings.
   - Surface findings with stable identifiers (`R1`, `R2`), severities, governing invariants, and locations.

2. **Mandatory Holistic Pattern Sweep & Sibling Symmetry Audit**
   - When a finding identifies a recurring smell or anti-pattern (such as test hooks in production files, leaky abstractions, unhandled errors, visibility mismatches, dead code, or compiler warnings), **do not scope the fix to only the cited line or file**.
   - Sweep the git diff and touched packages/crates for every sibling instance of that anti-pattern.
   - **Sibling Path Symmetry Audit:** When introducing an IoC seam, error boundary, or timeout to a capability, audit direct sibling dependencies in the same caller to prevent accidental architectural asymmetry. If a sibling is intentionally left concrete, record the rationale in the task brief or ADR.
   - Consolidate all discovered occurrences into one unified remediation scope (`R1.1`, `R1.2`, ...) so the builder resolves every site in one round.

3. **Human Selection Gate**
   - Present consolidated findings to the operator. Operator selects authorized must-fix IDs.

4. **Builder Remediation Dispatch (Mode B)**
   - Dispatch builder subagent in Mode B (Scoped Remediation) in an isolated worktree with the authorized IDs and full sibling site list.
   - Enforce Pure Production APIs (first-class Dependency Injection seams; zero test hooks or conditional test switches in `src/`), visibility matching signatures, and live caller wiring.
   - Builder reproduces the defect with a failing test, applies the minimal fix, compiles with zero warnings under fatal warning flags (`-D warnings` / `-Werror` / `strict: true`), and generates a Remediation Disposition Report.

5. **Confirm & Re-verify**
   - Inspector re-verifies the fix, validates zero compiler warnings, and confirms a clean diff and passing tests.
