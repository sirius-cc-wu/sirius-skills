---
type: "Capability Proposal"
title: "Boundary-Aware Rust Refactoring Design"
description: "Proposes a risk-driven cooperation contract between system analysis, native responsibility assignment, Rust ownership design, and vertical verification."
status: "proposed"
tags: [design, rust, refactoring, responsibilities, ownership, verification]
---

# Boundary-Aware Rust Refactoring Design

## Problem Statement

How might Sirius ensure that a complex Rust refactoring preserves its system
boundary and remains understandable to reviewers before ownership-driven code
is implemented, without imposing a complete object-design or artifact sequence
on every change?

The current risk-driven coordinator can classify a change as a refactoring,
select Rust lifecycle design, and proceed to implementation. That route can be
locally valid while still omitting the parent system scenario, module
responsibilities, or end-to-end verification boundary. A coding agent can then
produce ownership-safe Rust whose purpose, placement, and contribution to the
larger outcome remain difficult to review.

## Recommended Direction

Introduce a design-sufficiency gate for boundary-sensitive iterations. Treat a
refactoring as boundary-sensitive when it creates or moves a test seam,
composition root, backend, entrypoint, process-global dependency, runtime task,
resource owner, readiness condition, or cleanup boundary. Before implementation,
the coordinator must establish four linked views: the preserved system scenario,
native software responsibilities, Rust ownership and lifecycle, and verification
ownership. These are required questions, not mandatory standalone artifacts.

Use an ordered reasoning dependency with feedback:

```text
system boundary and preservation oracle
    -> native responsibility assignment
    -> Rust ownership and lifecycle realization
    -> vertical and focused verification
    -> reconciliation with the parent outcome
```

When Rust ownership makes a proposed responsibility awkward or unsafe, return
to responsibility design. When implementation changes a boundary or
collaboration, reconcile the system design. Completing a local abstraction
boundary may finish the current iteration. Treat it as an enabling result, not
completion of the parent outcome, until a representative end-to-end flow
successfully uses that boundary.

Keep `design-rust-lifecycles` as an implementation-facing specialist. Do not
make it responsible for requirements or system analysis. Broaden responsibility
reasoning so a responsibility can belong to a crate, module, type, function,
task, resource handle, adapter, or composition root. Preserve GRASP principles
where they help explain information ownership, coordination, coupling,
cohesion, creation, and variation.

## Key Assumptions to Validate

- [ ] A coordinator gate can distinguish a boundary-sensitive refactoring from
      a local mechanical refactoring without routing most Rust work through
      unnecessary analysis. Validate with contrasting routing and behavioral
      cases.
- [ ] A compact reviewer view containing system boundary, preserved scenario,
      native responsibilities, ownership transitions, and verification levels
      explains complex Rust changes better than a lifecycle design alone.
      Validate with a fixture that extracts a test environment or service
      entrypoint.
- [ ] Responsibility reasoning remains useful when its owner vocabulary is
      language-native rather than class-centered. Validate with Rust module,
      task, function, and handle assignments that do not introduce artificial
      objects or traits.
- [ ] Requiring a representative vertical oracle prevents a series of locally
      successful seams from being reported as the parent system outcome.
      Validate with a multi-iteration fixture whose component tests pass before
      its end-to-end scenario does.
- [ ] Existing artifact-selection rules can keep the design gate lightweight.
      Validate that agents update an existing owner or report the design
      conversationally instead of creating one file per view.

## MVP Scope

1. Add a boundary-sensitive refactoring check to
   `iterative-risk-driven-development`.
2. Require the iteration objective to identify:
   - the system boundary and representative behavior to preserve;
   - changed native responsibilities and dependency direction;
   - material Rust ownership, transfer, readiness, cancellation, and cleanup;
   - focused, integration, end-to-end, and human-owned verification; and
   - whether the result closes the parent outcome or only enables it.
3. Generalize `grasp-responsibility-design` guidance so language-native units
   are first-class responsibility owners. Decide through evaluation whether
   its object-centered name and routing description must also change.
4. Strengthen the `design-rust-lifecycles` input contract. When a
   boundary-sensitive objective lacks a current scenario, responsibility map,
   or verification boundary, return to the owning specialist instead of
   designing the lifecycle in isolation.
5. Add one behavioral composition case based on a host-safe Rust validation
   refactoring. Fail the case when the agent implements only configuration or
   lifecycle seams, loses the end-to-end oracle, leaves runtime ownership
   ambiguous, or declares the parent outcome complete prematurely.

The reviewer-facing result may be one embedded section, an update to an
existing design, or a conversational pre-implementation report. A new document
is not part of the completion criterion.

## Not Doing (and Why)

- Create Rust-specific copies of use-case, domain-model, system-sequence, or
  operation-contract skills. Their behavioral questions should remain
  language-neutral.
- Require a use case, domain model, SSD, operation contract, realization, and
  class diagram for every Rust refactoring. That would replace under-modeling
  with a mandatory artifact chain.
- Treat every refactoring as local or low risk merely because observable
  product behavior should remain unchanged. Test and runtime boundaries can
  change materially during behavior-preserving work.
- Merge system analysis, responsibility assignment, and Rust lifecycle design
  into one large Rust skill. Separate authority and feedback make omissions
  and design drift easier to detect.
- Require object or class designs where modules, functions, tasks, channels,
  enums, or resource handles express the actual software structure.
- Count a component seam, constructor, backend trait, or lifecycle handle as
  delivery of a broader host-safe or end-to-end outcome without vertical
  evidence.

## Open Questions

- Should `grasp-responsibility-design` be broadened in place, or should a new
  paradigm-neutral responsibility skill own modules, functions, tasks, and
  handles while GRASP remains an optional method?
- Which observable triggers are sufficient to classify an iteration as
  boundary-sensitive without using an arbitrary numeric threshold?
- Should infrastructure startup and shutdown postconditions remain in system
  design, or does Sirius need a small language-neutral runtime-operation
  contract distinct from domain-focused operation contracts?
- When should the reviewer-facing view become durable: before implementation,
  only after design stabilization, or only when an existing canonical owner
  already exists?
- Which behavioral fixture best distinguishes an enabling seam from a completed
  vertical outcome while remaining small enough for repeatable evaluation?
