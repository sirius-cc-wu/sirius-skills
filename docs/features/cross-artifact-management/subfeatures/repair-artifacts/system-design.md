# System Design: Repair Artifacts

## 1. Scope

`repair-artifacts` adds an explicit, conservative repair surface for the repo's
active registries. The first version should rebuild derived registry/readme
files from durable directories and valid metadata without rewriting semantic
planning documents.

## 2. Design Goals

- Use the owner scripts' existing row normalizers and registry writers.
- Default to dry-run output.
- Rebuild only active registries/readmes in v1.
- Leave malformed metadata as manual follow-up instead of guessing corrected
  content.

## 3. Proposed Shape

### 3.1 Repair inputs

- proposal directories plus `.proposal-meta.json`
- feature directories plus `.planning-meta.json`
- feature-local subfeature directories plus `.subfeature-meta.json`
- slice directories plus `.slice-meta.json`

### 3.2 Repair actions

For each selected artifact layer:

1. Discover on-disk directories from the shared inventory.
2. Read valid metadata.
3. Reconstruct normalized registry rows with the owner script's row shape.
4. Compare rebuilt rows to the current active registry.
5. Emit a repair plan in dry-run mode.
6. On `--apply`, write the rebuilt registry/readme with the owner script's
   registry writer.

### 3.3 First-version boundary

The first version repairs:

- `docs/proposals/README.md` + `registry.json`
- `docs/features/README.md` + `registry.json`
- feature-local `subfeatures/README.md` + `registry.json`
- `slices/README.md` + `registry.json`

It does not rewrite malformed metadata or freeform planning content.

## 4. CLI contract

```bash
sirius repair-artifacts
sirius repair-artifacts --artifact-type proposal --artifact-type slice
sirius repair-artifacts --apply --json
```

## 5. Validation strategy

- Fixture-driven tests should cover dry-run planning, proposal/feature registry
  regeneration, subfeature registry regeneration, and slice registry
  regeneration.
- Full repo validation remains `pytest -q`.

## 6. Risks

- Some broken metadata will still require manual repair.
- Apply mode must keep changes localized to the selected registry surfaces.
