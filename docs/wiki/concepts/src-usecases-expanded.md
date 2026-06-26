# src/ Use Cases (expanded)

This expanded page provides concrete examples and per-command sequence diagrams for key commands in src/. Each section includes a short example invocation, expected side-effects, and a PlantUML sequence diagram.

---

## 1) bootstrap
Example invocation:

    sirius bootstrap --feature my-feature

What happens:
- CLI discovers the bootstrap command and calls its main().
- The bootstrap command ensures planning registries exist and writes initial metadata and README files.
- Side-effects: files under planning/ are created or updated, .planning-meta.json written.

Sequence diagram:

```plantuml
!include ../diagrams/seq-bootstrap.puml
```

Files involved: src/sirius_skills/commands/bootstrap.py, lib/workflow_state/planning_repository.py, lib/workflow_state/markdown_repository.py

---

## 2) autoplan
Example invocation:

    sirius autoplan --feature my-feature --target slices

What happens:
- Command loads autoplan module which analyses feature content and suggests slice breakdowns.
- Uses semantic preview helpers to generate suggested plans.
- Side-effects: outputs suggested plan to stdout or writes draft artifacts.

Sequence diagram:

```plantuml
!include ../diagrams/seq-autoplan.puml
```

Files involved: src/sirius_skills/commands/autoplan.py, lib/workflow_state/semantic_preview.py

---

## 3) ship
Example invocation:

    sirius ship --slice slice-123

What happens:
- Ship command prepares a worktree, applies changes, and records runtime checkpoints/events.
- Side-effects: worktree session records, checkpoints, event log entries, artifacts moved to execution registry.

Sequence diagram:

```plantuml
!include ../diagrams/seq-ship.puml
```

Files involved: src/sirius_skills/commands/ship.py, lib/workflow_runtime/worktree_session.py, lib/workflow_runtime/event_log.py

---

## 4) scaffold-design
Example invocation:

    sirius scaffold-design --feature my-feature

What happens:
- Scaffold command creates design scaffolding, READMEs, and initial planning registry entries.
- Side-effects: README.md, registry.json, .planning-meta.json and example files created under the feature directory.

Sequence diagram:

```plantuml
!include ../diagrams/seq-scaffold_design.puml
```

Files involved: src/sirius_skills/commands/scaffold_design.py, lib/workflow_state/planning_repository.py, lib/workflow_state/markdown_repository.py

---

## 5) validate-workflow-state
Example invocation:

    sirius validate-workflow-state --scope all

What happens:
- Validate command reads persisted workflow state files and runs transition checks to ensure consistency.
- Side-effects: validation report printed; exit code != 0 on failure.

Sequence diagram:

```plantuml
!include ../diagrams/seq-validate-workflow-state.puml
```

Files involved: src/sirius_skills/commands/validate_workflow_state.py, lib/workflow_state/transitions.py, lib/workflow_state/storage.py

---

## Notes & next steps
- These diagrams and examples are generated from a quick code inspection; commands may accept additional flags and behave differently in edge cases.
- Next: auto-generate sequence diagrams per-command programmatically by parsing command modules to extract call targets.

(Generated automatically.)
