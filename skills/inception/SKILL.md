---
name: inception
description: Guides the Unified Process inception phase. Use when establishing a project's high-level vision, feasibility, business case, basic scope, key risks, and defining iteration plans to transition to elaboration.
---

# Inception

## Overview

Inception is the initial short step to establish a common vision, basic scope, and feasibility for a project. It is not the time to define all requirements, generate reliable plans, or design the architecture. The goal is to decide if the project is worth a serious investigation in the elaboration phase.

## When to Use

- Establishing the initial vision and business case for a new system or major initiative.
- Estimating feasibility (buy vs. build, order-of-magnitude cost, alignment on goals).
- Identifying initial primary actors and the list of expected use cases.
- Estimating technical, business, resource, and schedule risks at a high level.
- Setting up the development environment or customizing the UP Development Case for the project.
- Preparing the iteration plan for the first elaboration iteration.
- Do not use for defining detailed requirements, creating reliable plans/estimates, or designing the architecture (these belong to Elaboration).

## Workflow

1. **Establish the Vision and Business Case.** Envision high-level goals, key constraints, and business justification (Vision and Business Case artifacts).
2. **Determine Feasibility.** Evaluate technical feasibility, buy vs. build decisions, and order-of-magnitude (unreliable) cost ranges.
3. **Identify System Scope and Actors.** List primary actors and expected use cases. Write perhaps 10-20% of use cases in detail to obtain realistic insight into scope, leaving the rest as names.
4. **Identify Critical Non-Functional Requirements.** Document key non-functional requirements (Supplementary Specification) that have major architectural impact.
5. **Establish Glossary and Key Terminology.** Capture crucial domain terms to align stakeholders.
6. **Construct the Risk List.** Identify major technical, business, resource, and schedule risks, along with mitigation strategies.
7. **Build Proof-of-Concepts.** Create low-fidelity prototypes or run programming experiments for "show stopper" technical questions if needed.
8. **Plan the Next Step.** Define the iteration plan for the first elaboration iteration. Estimate a low-precision guess for elaboration phase duration/effort (Phase Plan).
9. **Define the Development Case.** Customize the UP steps and artifacts to fit the specific project's scale and constraints.

## Red Flags

- Inception lasts more than a few weeks.
- Attempting to define most of the requirements.
- Expecting project plans or estimates to be reliable.
- Defining the architecture (which should be done iteratively in Elaboration).
- Having no Business Case or Vision artifact.
- Writing all use cases in detail (or writing none of them in detail).
- Believing the sequence of work must be: 1) define all requirements; 2) design architecture; 3) implement.

## Verification

- [ ] A clear business case and high-level vision have been established.
- [ ] Basic project feasibility (technical, financial, buy/build) has been evaluated.
- [ ] Primary actors and expected use cases have been identified.
- [ ] At least 10% (but no more than 20%) of the use cases have been written in detail to validate scope.
- [ ] Key non-functional requirements with major architectural impact are documented in the Supplementary Specification.
- [ ] Major technical, business, resource, and schedule risks are recorded in a Risk List.
- [ ] A low-precision phase plan/effort guess for Elaboration is defined.
- [ ] An Iteration Plan for the first elaboration iteration is created.
- [ ] The UP Development Case has been customized for the project's scale and constraints.
