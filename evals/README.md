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

The active pilot covers:

- `assess-development-input`;
- `select-technical-artifacts`;
- `design-repository-artifact-layout`;
- `iterative-risk-driven-development`;
- `define-project-vision`;
- `specify-quality-constraints`;
- `operation-contracts`;
- `design-software-architecture`;
- `grasp-responsibility-design`;
- `design-rust-lifecycles`;
- `behavior-preserving-refactoring`;
- `software-design-language-adaptation`;
- `use-case-modeling`;
- `walkthrough-me`; and
- `uml-class-diagram-design`.

The fixture-backed cases distinguish three outcomes. One boundary-sensitive
Rust refactoring case requires the coordinator to retain the system boundary,
native responsibilities, ownership consequences, verification ownership, and
open parent outcome before more implementation. One visual case selects a
focused class view for justified stateful object design. One contract case adds
declarative state effects to an existing feature-analysis aggregate without
creating code, implementation design, or a second artifact. A provisional
support-envelope case checks that one reported model does not silently define a
broader supported population, capability source, verification set, or parent
completion claim.

## Case Format

Keep one JSON file per evaluated skill at
`evals/cases/<skill-name>.json`:

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
      "trust_level": "provisional"
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
require or forbid literal fragments in a named output file; it is suitable for
checking that a PlantUML block and requested diagram kind exist, not for
judging whether the diagram communicates well. The deterministic tier
validates the case shape but does not claim the behavior passed.

`workspace_mode` defaults to `mutable`, which requires at least one
`allowed_mutations` pattern. Set it to `read-only` only when unresolved intent
or authority should prevent every repository change; both `allowed_mutations`
and `required_mutations` must then be empty lists. The executor still receives
a writable disposable workspace so attempted mutations are observable and fail
the case rather than being hidden by sandbox denial.

A file assertion examines the whole file by default. Set
`"scope": "plantuml"` for Markdown diagram artifacts so `contains` and
`not_contains` inspect only complete fenced `plantuml` blocks. This prevents
ordinary prose such as “no class diagram” from satisfying or violating a
diagram-notation assertion. A missing or unterminated PlantUML fence fails the
assertion.

`trace_assertions` can mechanically check selected JSONL event ordering. The
supported `red_green` assertion requires every `command_contains` fragment to
appear in a command. A matching nonzero command must complete before the first
file change matching `mutation_patterns`, and a matching zero-exit command
must complete after the last matching change. This establishes red–mutation–
green ordering; it does not prove that the failing command discriminated the
intended behavior.

Each result records the executor host and its `--version` output when
available, the explicitly requested model, any model name explicitly reported
by the JSONL trace, and reported token usage. If the trace does not identify
the resolved model, `observed_model` remains null; the runner does not infer it
from local configuration. Usage distinguishes cached, cache-write, uncached,
output, and reasoning tokens. Missing usage remains missing rather than being
counted as zero.

Each per-run `result.json` also records `final_response`, taken from the last
non-empty completed `agent_message` in a valid Codex JSONL trace. It remains
`null` when the executor reports no completed agent response. This field makes
manual review and future semantic evaluation direct, but it is supporting
evidence and does not affect the mechanical result.

An optional `semantic_rubric` is a list of independently judgeable criteria
with stable opaque IDs:

```json
"semantic_rubric": [
  {
    "id": "requests-governing-decision",
    "criterion": "The response asks which policy governs cancellation after submission."
  }
]
```

Use it only for response qualities that deterministic workspace, command,
file, or trace evidence cannot establish. IDs must be unique within the case.
The initial rubric pilot used a read-only workflow-reentry case. No active
pilot case currently declares a semantic rubric.

`semantic_controls` provide reviewed candidate responses with an expected
boolean for every rubric criterion. Each control repeats the rubric IDs in
rubric order so omissions and accidental remapping fail validation. Include at
least one response that should satisfy the rubric and one realistic failure
that should not; across the controls, every criterion must exercise both
`true` and `false`:

```json
"semantic_controls": [
  {
    "id": "complete-reentry",
    "response": "The approved policies conflict. Which one governs? I made no changes.",
    "expected_criteria": [
      {"id": "requests-governing-decision", "passed": true}
    ]
  },
  {
    "id": "unauthorized-choice",
    "response": "I selected one policy and implemented it.",
    "expected_criteria": [
      {"id": "requests-governing-decision", "passed": false}
    ]
  }
]
```

## Run a Behavioral Case

Inspect the plan before spending model tokens:

```bash
just eval-behavior-dry-run \
  iterative-risk-driven-development \
  boundary-sensitive-rust-refactoring
```

Then run that explicitly selected case through the locally authenticated Codex
CLI:

```bash
just eval-behavior \
  iterative-risk-driven-development \
  boundary-sensitive-rust-refactoring
```

Pass a repetition count to measure stability without overwriting earlier
evidence:

```bash
just eval-behavior \
  iterative-risk-driven-development \
  boundary-sensitive-rust-refactoring \
  3
```

Cases with a `semantic_rubric` can run an additional opt-in judge. No active
pilot case currently declares one. After adding such a case, use:

```bash
just eval-behavior-judged SKILL CASE
```

The judge runs as a separate ephemeral Codex invocation in an empty temporary
Git repository with a read-only sandbox. It receives the task context, rubric,
and captured final response, but not the evaluated workspace. Candidate prose
is marked as untrusted input. Judge failures and negative judgments are
recorded for review and never change the mechanical pass or command exit code.

Before relying on a rubric diagnostically, run its controls without invoking
the coding agent:

```bash
just eval-judge-calibration SKILL CASE 3
```

Each control uses the same isolated judge prompt and receives its own trace.
The calibration command exits nonzero when a judge error or criterion mismatch
occurs and writes an ignored `summary.json` beneath `evals/results/`. That exit
status describes only the explicit calibration run; it never changes a
behavioral eval's mechanical result.

With a repetition count, every declared control runs that many times. The
summary records whether each control's verdict signature—judge status, ordered
criterion booleans, and any error—is stable, along with per-control match rate,
aggregate reported token usage, and duration statistics. Calibration passes
only when every judgment matches its reviewed criterion expectations;
stability is reported separately so a consistently wrong judge is not mistaken
for a calibrated one. Repeated agreement demonstrates basic polarity and
short-run consistency for the selected judge, not general accuracy or
independence from the evaluated model.

Compare the same controls across judge models when model-specific bias or cost
is material:

```bash
just eval-judge-comparison \
  SKILL \
  CASE \
  BASE_MODEL \
  COMPARISON_MODEL
```

The comparison runner preserves each model's normal calibration summary and
adds a matrix summary. It reports disagreements by control, repetition, status,
and criterion boolean; prose reasons are retained in the underlying traces but
do not define agreement. Per-model and aggregate token usage and duration make
the quality/cost tradeoff visible. All models remain diagnostic and
non-gating. The comparison command exits nonzero if any model misses a reviewed
expectation.

Behavioral execution is never part of `just validate`. The runner:

1. copies the declared fixture into a fresh temporary Git repository and
   commits it as the clean comparison baseline;
2. invokes `codex exec` ephemerally with JSONL output and a workspace-write
   sandbox;
3. supplies the selected `SKILL.md`, prompt, expectations, prohibitions, and
   checks as the evaluation prompt;
4. captures created, modified, and deleted files while ignoring tool caches;
5. rejects changes outside `allowed_mutations`, including every change in a
   read-only case, and reports missing `required_mutations`;
6. evaluates declared JSONL trace-order assertions;
7. checks required and forbidden output-file fragments;
8. runs declared verification commands without a shell;
9. extracts the final completed agent response as supporting evidence;
10. when explicitly enabled, evaluates the declared response rubric in an
    isolated read-only judge process; and
11. writes every trace and mechanical result to a unique run directory under
    ignored `evals/results/`, plus a batch summary with pass rate, mechanical
    outcome, changed-path/kind, and execution-environment stability, aggregate
    reported token usage, and duration statistics, before deleting each
    temporary workspace.

Use the lower-level command when a model override, timeout, or retained
workspace is needed:

```bash
PYTHONPATH=src python3 -m sirius_skills.commands.run_evals \
  --behavioral iterative-risk-driven-development \
  --case boundary-sensitive-rust-refactoring \
  --model MODEL \
  --repeat 3 \
  --timeout 900 \
  --keep-workspace
```

Inspect a calibration plan without running either model:

```bash
PYTHONPATH=src python3 -m sirius_skills.commands.run_evals \
  --behavioral SKILL \
  --case CASE \
  --calibrate-judge \
  --judge-model JUDGE_MODEL \
  --repeat 3 \
  --dry-run
```

Add one or more comparison models with repeated
`--compare-judge-model MODEL`. An explicit `--judge-model` or `--model` supplies
the base model.

Each run reports only a **mechanical pass**: the executor exited normally,
mutation boundaries held, required changes occurred or read-only state was
preserved, and declared mechanical assertions and commands passed. The batch
summary identifies variation; it does not turn repeated agreement into
semantic proof. Without `--judge`, semantic expectations remain explicitly
`ungraded`. With it, `result.json` records each criterion verdict and reason,
judge errors, model metadata, duration, usage, prompt, response, and a separate
judge trace. Primary-run usage totals do not include judge usage. Treat these
judgments as diagnostic evidence rather than an authority for mutations,
verification, or process exit. Do not report a mechanical pass or judge pass
alone as proof that the skill behaved correctly.

## Scoring Boundaries

The runner uses a dependency-free, lightly normalized TF-IDF approximation over
skill names and descriptions. It reports the positive rank-one rate for trend
visibility but gates only each case's declared `top_k`, owned negatives, and
severe description collisions.

A routing failure normally means one of three things: the skill description
lacks vocabulary users employ, a neighboring boundary is unclear, or the case
does not represent the responsibility it declares. Diagnose the evidence; do
not weaken a case solely to make the aggregate score increase.
