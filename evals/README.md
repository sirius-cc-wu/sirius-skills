# Skill Evals

Sirius evaluates whether realistic user prompts can distinguish neighboring
skill descriptions before spending model tokens. These deterministic checks
are routing tripwires, not proof that an agent will select or follow a skill.

## Run the Free Tier

```bash
just eval-routing
```

`just validate` includes the same command. The runner reads every deployable
skill's frontmatter, evaluates the cases in `evals/cases/`, reports missing
coverage as warnings, and exits nonzero for schema, routing, owner, or severe
description-collision failures.

The active catalog covers all 17 deployable skills:

- `create-pr`
- `walkthrough-me`
- `github-issue-workflow`
- `review-pr`
- `spec-qualification`
- `audit-vestigial-contracts`
- `audit-pr-scope`
- `select-technical-artifacts`
- `design-repository-artifact-layout`
- `assess-development-input`
- `vision`
- `specify-quality-constraints`
- `software-design-language-adaptation`
- `design-rust-lifecycles`
- `behavior-preserving-refactoring`
- `architecture-decision-records`
- `type-anchored-spec`

### Fixture-Backed Behavioral Evaluations

High-fidelity behavioral evaluations run against language-agnostic or Bun/TypeScript
disposable fixtures under `evals/fixtures/`:

1. **PR Scope Mismatch (`evals/fixtures/pr-scope-mismatch`)**:
   Tests `audit-pr-scope` in `read-only` workspace mode against a pull request with
   extensive speculative abstractions (an unrequested event-bus and plugin manager)
   added onto a minimal bugfix. Checks that the skill identifies the core motivating
   incident, flags overengineering, and recommends vertical re-scoping slices without
   modifying code.
2. **Refactor Boundary (`evals/fixtures/refactor-boundary`)**:
   Tests `behavior-preserving-refactoring` on a clean TypeScript/Bun project with green
   tests (`bun test`). Evaluates relocating an misplaced pricing calculation from a service
   to an entity domain owner while maintaining 100% test pass rates and zero public API regressions.
3. **Typestate Workflow (`evals/fixtures/typestate-workflow`)**:
   Tests `type-anchored-spec` on translating an approved order fulfillment state machine
   into Rust typestate and phantom-type compile-time guarantees, preventing illegal state
   transitions structurally at compile time.

## Case Format

Keep one JSON file per evaluated skill at `evals/cases/<skill-name>.json`:

```json
{
  "skill_name": "behavior-preserving-refactoring",
  "trigger": {
    "positive": [
      {
        "prompt": "Move this cohesive responsibility to its established owner without changing behavior",
        "top_k": 3
      }
    ],
    "negative": [
      {
        "prompt": "Design exact Rust resource ownership and cleanup",
        "owner": "design-rust-lifecycles"
      }
    ]
  },
  "evals": [
    {
      "id": "local-verified-transformation",
      "prompt": "Correct this dependency direction behind green tests.",
      "expected_output": "One verified structural design transformation preserves behavior.",
      "expectations": [
        "Focused and regression checks remain green"
      ],
      "prohibitions": [
        "Do not change required behavior"
      ],
      "allowed_mutations": [
        "src/**",
        "tests/**"
      ],
      "required_mutations": [
        "src/domain.ts",
        "src/service.ts"
      ],
      "checks": [
        ["bun", "test"]
      ],
      "fixture": "refactor-boundary",
      "trust_level": "fixture-backed"
    }
  ]
}
```

### Routing Fields

- `skill_name` must match both the filename and a deployable skill.
- A positive prompt must rank its skill within `top_k`, which defaults to
  three. Use ordinary user language rather than copying the skill description.
- A negative prompt must declare the skill that owns it. The declared owner
  must outrank the case skill, preventing empty-vocabulary prompts from passing
  accidentally.
- The pilot minimum is three positive prompts, two owned negative prompts, and
  one behavioral case. Missing catalog coverage and sub-minimum cases are
  warnings while the pilot matures.

### Behavioral Fields

`evals[]` records the model-executed behavioral oracle. Every entry has an
opaque, stable `id`, a prompt, an outcome-oriented `expected_output`, and one
or more behavioral `expectations`. Optional `prohibitions` and
`allowed_mutations` declare negative behavior and workspace authority.

Behavioral entries remain `provisional` until they have a disposable fixture.
A fixture-backed entry also declares `fixture`, `required_mutations`, optional
argument-vector `checks`, and optional `file_assertions`. A file assertion can
require or forbid literal fragments in a named output file.

`workspace_mode` defaults to `mutable`, which requires at least one
`allowed_mutations` pattern. Set it to `read-only` only when unresolved intent
or authority should prevent every repository change; both `allowed_mutations`
and `required_mutations` must then be empty lists.

### Semantic Rubrics and Calibrated Controls

An optional `semantic_rubric` defines independently judgeable criteria with stable opaque IDs:

```json
"semantic_rubric": [
  {
    "id": "identifies-motivating-problem",
    "criterion": "The response identifies the motivating problem as the query cache leak on timeout (Issue #180)."
  }
]
```

`semantic_controls` provide reviewed candidate responses with an expected
boolean for every rubric criterion. Each control repeats the rubric IDs in
rubric order so omissions and accidental remapping fail validation. Across the
controls, every criterion must exercise both `true` and `false`:

```json
"semantic_controls": [
  {
    "id": "ctrl-pass-complete-audit",
    "response": "The motivating problem is Issue #180. The delivered PR introduces severe over-engineering in the event bus and plugin manager.",
    "expected_criteria": [
      {"id": "identifies-motivating-problem", "passed": true}
    ]
  },
  {
    "id": "ctrl-fail-rubber-stamp",
    "response": "PR looks great! Merge approved without changes.",
    "expected_criteria": [
      {"id": "identifies-motivating-problem", "passed": false}
    ]
  }
]
```

## Run a Behavioral Case

Inspect the plan before spending model tokens:

```bash
just eval-behavior-dry-run \
  behavior-preserving-refactoring \
  local-verified-transformation
```

Then run that explicitly selected case through the locally authenticated Codex CLI:

```bash
just eval-behavior \
  behavior-preserving-refactoring \
  local-verified-transformation
```

Pass a repetition count to measure stability without overwriting earlier evidence:

```bash
just eval-behavior \
  behavior-preserving-refactoring \
  local-verified-transformation \
  3
```

Cases with a `semantic_rubric` can run an additional opt-in judge:

```bash
just eval-behavior-judged audit-pr-scope audit-pr-scope-mismatch
```

Before relying on a rubric diagnostically, run its controls to calibrate the judge:

```bash
just eval-judge-calibration audit-pr-scope audit-pr-scope-mismatch 3
```

Compare the same controls across judge models when model-specific bias or cost is material:

```bash
just eval-judge-comparison \
  audit-pr-scope \
  audit-pr-scope-mismatch \
  BASE_MODEL \
  COMPARISON_MODEL
```

## CLI Invocations

Use the lower-level CLI command when a model override, timeout, or retained workspace is needed:

```bash
bun scripts/run_evals.ts \
  --behavioral behavior-preserving-refactoring \
  --case local-verified-transformation \
  --model MODEL \
  --repeat 3 \
  --timeout 900 \
  --keep-workspace
```

Inspect a calibration plan without running either model:

```bash
bun scripts/run_evals.ts \
  --behavioral audit-pr-scope \
  --case audit-pr-scope-mismatch \
  --calibrate-judge \
  --judge-model JUDGE_MODEL \
  --repeat 3 \
  --dry-run
```
