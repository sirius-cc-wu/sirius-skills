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

The initial pilot covers:

- `iterative-up-analysis-design`;
- `use-case-modeling`;
- `test-driven-implementation`;
- `recover-system-behavior`;
- `reconcile-recovered-design`; and
- `commit`.

## Case Format

Keep one JSON file per evaluated skill at
`evals/cases/<skill-name>.json`:

```json
{
  "skill_name": "test-driven-implementation",
  "trigger": {
    "positive": [
      {
        "prompt": "Reproduce this bug with a failing test before fixing it",
        "top_k": 3
      }
    ],
    "negative": [
      {
        "prompt": "Refactor this duplication without changing behavior",
        "owner": "behavior-preserving-refactoring"
      }
    ]
  },
  "evals": [
    {
      "id": "bug-fix-discrimination",
      "prompt": "Fix the reported invoice rounding defect.",
      "expected_output": "The defect is reproduced, minimally fixed, and regression-tested.",
      "expectations": [
        "A check discriminates the defect before the production fix"
      ],
      "prohibitions": [
        "Do not weaken an existing valid expectation"
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

`evals[]` records the future model-executed oracle. Every entry has an opaque,
stable `id`, a prompt, an outcome-oriented `expected_output`, and one or more
behavioral `expectations`. Optional `prohibitions` and `allowed_mutations`
declare negative behavior and workspace authority.

Behavioral entries remain `provisional` until they have a disposable fixture.
A fixture-backed entry also declares `fixture`, `required_mutations`, and
argument-vector `checks`. The deterministic tier validates their shape but
does not claim they passed.

## Run a Behavioral Case

Inspect the plan before spending model tokens:

```bash
just eval-behavior-dry-run test-driven-implementation bug-fix-discrimination
```

Then run that explicitly selected case through the locally authenticated Codex
CLI:

```bash
just eval-behavior test-driven-implementation bug-fix-discrimination
```

Behavioral execution is never part of `just validate`. The runner:

1. copies the declared fixture into a fresh temporary Git repository;
2. invokes `codex exec` ephemerally with JSONL output and a workspace-write
   sandbox;
3. supplies the selected `SKILL.md`, prompt, expectations, prohibitions, and
   checks as the evaluation prompt;
4. captures created, modified, and deleted files while ignoring tool caches;
5. rejects changes outside `allowed_mutations` and missing
   `required_mutations`;
6. runs declared verification commands without a shell; and
7. writes the trace and mechanical result under the ignored `evals/results/`
   directory before deleting the temporary workspace.

Use the lower-level command when a model override, timeout, or retained
workspace is needed:

```bash
PYTHONPATH=src python3 -m sirius_skills.commands.run_evals \
  --behavioral test-driven-implementation \
  --case bug-fix-discrimination \
  --model MODEL \
  --timeout 900 \
  --keep-workspace
```

The result reports only a **mechanical pass**: the executor exited normally,
mutation boundaries held, required changes occurred, and declared commands
passed. The full JSONL trace and semantic expectations are preserved, but
expectations and prohibitions remain explicitly `ungraded` until a trustworthy
semantic evaluator is implemented. Do not report a mechanical pass as proof
that the skill behaved correctly.

## Scoring Boundaries

The runner uses a dependency-free, lightly normalized TF-IDF approximation over
skill names and descriptions. It reports the positive rank-one rate for trend
visibility but gates only each case's declared `top_k`, owned negatives, and
severe description collisions.

A routing failure normally means one of three things: the skill description
lacks vocabulary users employ, a neighboring boundary is unclear, or the case
does not represent the responsibility it declares. Diagnose the evidence; do
not weaken a case solely to make the aggregate score increase.
