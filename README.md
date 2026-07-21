# sirius-skills

`sirius-skills` is a focused collection of four generic repository workflow
skills. The former spec-driven development (SDD) catalog has been retired and
is no longer included in the managed install.

## Available skills

| Skill | Purpose |
|---|---|
| [`simplify`](skills/simplify/SKILL.md) | Simplify branch or pull-request changes without intentionally changing behavior. |
| [`create-pr`](skills/create-pr/SKILL.md) | Create a well-scoped GitHub pull request with convention-aware titles and validation. |
| [`commit`](skills/commit/SKILL.md) | Review, verify, stage, and commit an intentional change set. |
| [`governance-update`](skills/governance-update/SKILL.md) | Tighten durable repository guidance when repeated drift reveals a policy gap. |

These are the only skills declared by `managed_skills` in `justfile` and the
only skills registered by the supported install flow.

## Install

Install the managed skills globally for the configured agents:

```bash
just install
```

Remove the managed skills later with:

```bash
just uninstall
```

The explicit packaged aliases remain available and use the same flow:

```bash
just install-packaged
just uninstall-packaged
```

Installation refreshes shared references directly from the checkout, then uses
`npx skills` to register only the four skills listed above. It does not install
the repository's legacy Python helper package.

## Conventions

`commit` and `create-pr` can read `.skills/conventions.json` when a repository
needs project-specific formatting. Supported fields include:

- `commit_format`
- `pr_title_format`
- `branch_extract_pattern`
- `id_pattern`

Keep shared skills generic. Put repository-specific naming and tracker rules in
configuration instead of hardcoding them into a skill.

## Usage guidance

See [`SKILLS_METHODOLOGY.md`](SKILLS_METHODOLOGY.md) for how the four skills fit
together and [`PROMPT_GUIDE.md`](PROMPT_GUIDE.md) for example requests.

The material under `docs/features/`, `docs/wiki/`, and `slices/` records the
repository's earlier SDD implementation history. It is retained as historical
context, not as the current skill catalog or recommended operating workflow.
