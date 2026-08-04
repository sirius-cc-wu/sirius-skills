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

Behavioral entries remain `provisional` until a disposable fixture and runner
can observe tool events, commands, workspace mutations, and verification
results. The deterministic tier validates their shape but does not claim they
passed.

## Scoring Boundaries

The runner uses a dependency-free, lightly normalized TF-IDF approximation over
skill names and descriptions. It reports the positive rank-one rate for trend
visibility but gates only each case's declared `top_k`, owned negatives, and
severe description collisions.

A routing failure normally means one of three things: the skill description
lacks vocabulary users employ, a neighboring boundary is unclear, or the case
does not represent the responsibility it declares. Diagnose the evidence; do
not weaken a case solely to make the aggregate score increase.
