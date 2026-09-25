---
name: audit-pr-scope
description: >-
  Audits whether a pull request's scope matches its motivating problem.
  Use when asked if a PR is overengineered or underengineered, to evaluate PR scope creep,
  diff signal-to-noise ratio, or when planning to re-scope a large PR into vertical slices.
---

# Audit Pull Request Scope

## Role

Orchestrates a read-only audit evaluating whether a pull request's scope and depth match the motivating problem it intends to solve:
1. Isolate the minimal motivating problem, root incident, or requirements hypothesis.
2. Filter diff noise and measure the signal-to-noise ratio.
3. Concurrently audit for **over-engineering** (incidental complexity, excess concurrency, speculative abstractions, diff churn) and **under-engineering** (violated non-functional requirements, real-time safety violations, untruthful telemetry, missing edge handling).
4. Propose an actionable, vertical re-scoping plan (e.g., Slice A for immediate low-risk problem solving vs. Slice B for decoupled/hardened capabilities).

Does not prescribe a specific reviewer or model. Maintains strict read-only boundaries.

## When to Use

- Use when asked: *"Does the scope of this PR match the problem it's trying to solve?"*
- Use when evaluating whether a PR is overengineered, underengineered, or both.
- Use to assess PR scope creep, disproportionate process ceremony, or diff churn.
- Use when preparing to decompose a large, monolithic PR into reviewable vertical slices.
- Do not use for line-by-line syntax or style reviews (use `code-review-and-quality`).
- Do not modify or publish comments without explicit user consent.

## Workflow

### 1. Establish review context and isolate motivating problem
- Retrieve PR metadata, description, commits, and linked artifacts:
  ```bash
  gh pr view <number> --json number,title,body,author,baseRefName,headRefName,commits,files
  ```
- Extract the **Motivating Problem**:
  - What exact incident, bug report, customer issue, or ADR triggered this change?
  - What is the minimal capability required to resolve that specific problem?
  - What non-negotiable domain constraints apply (e.g., hard real-time cycle deadlines, thread safety, memory boundaries, flash endurance)?

### 2. Measure diff signal-to-noise and filter churn
- Inspect file stats and diffs without whitespace:
  ```bash
  gh pr diff <number> --name-only
  gh pr diff <number> --patch
  ```
- Distinguish substantive changes from churn:
  - Whole-file re-indentation, automated formatter churn, or unrelated cleanups.
  - Test harness or scaffolding additions versus production logic changes.
  - Process artifact volume (ADRs, SSDs, design models, qualification reports) relative to the functional delta.

### 3. Dual-axis depth audit (over- vs. under-engineering)
Audit the change across two complementary failure modes:

#### Axis A: Over-engineering (Incidental Complexity)
- **Excessive Concurrency & State:** Dedicated OS threads, locks, condition variables, or atomics where a simple monotonic timestamp check or synchronous caller deadline suffices.
- **Speculative Abstractions & Mocks:** Generic plug-in architectures, synthetic hardware simulators, or fake mock features that leak into production dependency graphs.
- **Process & Scaffolding Ceremony:** Generating extensive architectural artifacts (formal specs, multiple qualification reports) for a minor operational toggle or bug fix.
- **Feature & UI Bloat:** Adding secondary UI widgets, real-time gauges, or configuration knobs beyond what is needed to verify or solve the motivating case.

#### Axis B: Under-engineering (Critical Invariants Missed)
- **Non-Functional Violations:** Introducing blocking locks, file I/O, string formatting, or unbounded allocations inside critical paths (e.g., a cyclic 1 ms real-time controller loop).
- **Untruthful Telemetry / Fake Feedback:** Reading dummy placeholders, unverified caches, or commanded values rather than actual hardware register feedback.
- **Early-Drop Blind Spots:** Failing to capture failures or state transitions that occur prior to entering the recorded pipeline (e.g., early buffer rejection).
- **Contention Cascades:** Holding global locks across network broadcasts, IPC, or external I/O.

### 4. Formulate vertical re-scoping plan
When a PR is oversized or entangled, decompose it into cleanly separated vertical slices:
- **Slice A (Minimal Viable Solution):** The narrowest, lowest-risk change that directly answers the motivating problem. Keeps writers off critical/real-time paths and strips formatting churn.
- **Slice B (Decoupled / Hardened Telemetry):** Advanced cyclic monitoring, hardware telemetry, or complex UI, isolated via lock-free buffers (e.g., SPSC queues) and decoupled from the core fix.
- Provide a Mermaid flowchart illustrating the decoupled architecture.

### 5. Report findings

Present the review using the following structured template:

```markdown
## Scope Audit: Does the PR's size fit the problem?

**Verdict:** [Matched / Over-engineered / Under-engineered / Both]

### 1. Motivating Problem vs. Delivered Scope
- **Motivating Problem:** [1-2 sentences identifying root cause/trigger]
- **Delivered Scope:** [Summary of files, lines, and broad feature sets added]

### 2. Over-engineering (Incidental Complexity)
| Area | Observation |
|---|---|
| Diff noise & churn | [Formatting, re-indentation, unrelated edits] |
| Concurrency / State | [Unnecessary threads, locks, duplicate paths] |
| Scaffolding / Mocks | [Test frameworks, production leakage] |
| Process ceremony | [Disproportionate documentation/qualification] |

### 3. Under-engineering (Critical Invariants Missed)
- **Critical Path Safety:** [Violations of real-time, memory, or safety constraints]
- **Telemetry Truthfulness:** [Dummy fallbacks, unverified states]
- **Coverage Blind Spots:** [Missing early rejection or drop points]

### 4. Recommended Re-scoping
\`\`\`mermaid
flowchart LR
  [Mermaid diagram showing Slice A vs Slice B decoupling]
\`\`\`
- **Slice A (Immediate / Low Risk):** [Scope of minimal fix]
- **Slice B (Hardened / Decoupled):** [Scope of advanced capabilities]
```

## Failure Handling

- If the motivating problem or issue context cannot be retrieved, ask the user to clarify the core objective before issuing an audit verdict.
- Never modify branches, files, or post GitHub comments without explicit user authorization.
