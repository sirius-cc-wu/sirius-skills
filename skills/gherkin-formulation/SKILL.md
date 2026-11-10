---
name: gherkin-formulation
description: Formulate discovered examples and rules into clear, declarative, executable Gherkin specifications (Given-When-Then). Use after requirements discovery (Example Mapping or Feature Mapping) and before test automation or TDD implementation to create living documentation.
---

# Gherkin Formulation

## Formulation Workflow

Formulation translates concrete examples and business rules discovered during Three Amigos workshops into unambiguous, executable specifications using standard Gherkin syntax (`Feature`, `Rule`, `Scenario`, `Scenario Outline`).

Formulation happens **after** discovery, typically in pairs (e.g. developer and tester), avoiding syntax debates during broader team discovery.

---

### 1. The BRIEF Principles of Good Scenarios

Every scenario must adhere to the BRIEF quality criteria:

* **Business Language:** Written using domain vocabulary (Ubiquitous Language) understood by business stakeholders, not technical or implementation jargon.
* **Real Data:** Illustrates behavior with concrete, representative sample values rather than abstract variables or placeholders.
* **Intention-Revealing:** Expresses *what* the system does and *why*, rather than *how* the UI or technical plumbing operates.
* **Essential:** Omits incidental details, setup noise, or secondary parameters that do not directly contribute to the rule being illustrated.
* **Focused:** Verifies exactly one business rule or scenario variation per scenario.

---

### 2. Declarative vs. Imperative Formulation

The single most critical rule of Gherkin authoring is **declarative over imperative style**:

```gherkin
# ❌ ANTI-PATTERN: Imperative / UI-Coupled (Fragile, Incidental)
Scenario: User logs in and changes password
  Given I navigate to "http://localhost:3000/login"
  And I fill in "#username" with "alice"
  And I fill in "#password" with "Secret123"
  And I click on "button.login-submit"
  And I wait for the page to load
  And I click on "nav a.settings"
  ...

# ✅ BEST PRACTICE: Declarative / Domain-Focused (Durable, Clear)
Rule: Account passwords must meet complexity requirements

  Scenario: Password changed successfully
    Given an authenticated standard user "Alice"
    When Alice changes her password to "NewValidPass!9"
    Then her credentials are updated
    And a security alert is dispatched to her registered email
```

---

### 3. Structural Gherkin Patterns

```gherkin
Feature: Desktop Target Handoff
  As a developer reviewing repository documentation
  I want CLI target commands to open in my active desktop window
  So that I avoid browser tab sprawl

  Background:
    Given a running Lens desktop application instance for user "sirius"

  Rule: Subsequent invocations reuse the active application window

    Scenario: Forward new target to active window
      When the user executes "lens docs/spec.md" from "/home/user/project"
      Then the active desktop window appends a tab for "docs/spec.md"
      And the Lens application window gains OS focus
      And the CLI command exits with code 0

    Scenario Outline: Reject unauthorized or out-of-root targets
      When the user executes "<target>" from "/home/user/project"
      Then the CLI reports "<error_message>" to stderr
      And the CLI exits with code 1
      And the active desktop window tabs remain unchanged

      Examples:
        | target            | error_message                          |
        | ../outside/foo.md | target is outside canonical root       |
        | missing.md        | target does not exist or is unreadable |
```

* **`Feature`**: High-level capability and business benefit (As a / I want / So that).
* **`Background`**: Common preconditions shared by *all* scenarios in the feature. Keep short; do not hide essential scenario context.
* **`Rule`**: Groups scenarios by the specific business rule or invariant they illustrate (supported in Gherkin v6+).
* **`Scenario Outline` / `Examples`**: Use for parameterized testing of multiple inputs against the same behavioral outcome.

---

## Agent Adaptation

These conventions adapt Gherkin formulation to an AI assistant:

* **Require Prior Discovery:** Do not invent Gherkin scenarios from vacuum or raw specifications. Start from completed `example-mapping` or `feature-mapping` outputs.
* **Purge Incidental Mechanics:** Automatically strip button clicks, CSS selectors, URL routing mechanics, or database column names unless the system under test is an HTTP router or database engine itself.
* **Strict 1:1 Rule Mapping:** Structure `.feature` files using `Rule:` blocks that mirror the rules discovered in the discovery map.
* **Downstream Handoff:**
  * Package formulated `.feature` files into task specifications for Workers (`test-driven-development`).
  * Use the formulated scenario checklist during `spec-qualification` to audit test coverage in the Worker's diff.

---

## Source

Distilled from Seb Rose, Gáspár Nagy, and Matt Wynne, *Formulation: Document examples with Given/When/Then* (The BDD Books, 2021) and John Ferguson Smart, *BDD in Action* (2nd Edition, Manning Publications). The agent conventions above are adaptations, not direct claims from the authors.
