# System Design: Installation and Configuration

## Overview

Installation and configuration form the repository integration layer. The
`Makefile` now exposes one packaged install path, while the `.skills/`
directory provides separate
configuration surfaces for planning layout, execution layout, and naming
conventions. Project-local extensions live in `.skills/plugins/` and are only
used when a specific skill explicitly opts in.

## Related Stories

- `IC-01`: maintain one managed install and uninstall path for the shared skills
- `IC-02`: keep planning and execution layout config separate and explicit
- `IC-03`: store naming and ID conventions in a dedicated config file
- `IC-04`: document a plugin convention for project-local extensions

## Key Components

- **Managed install entrypoint**: `Makefile`
- **Planning layout config**: `.skills/planning.json`
- **Execution layout config**: `.skills/execution.json`
- **Conventions config**: `.skills/conventions.json`
- **Project-local extensions**: `.skills/plugins/`
- **Consumer skills**: guide-planning, guide-execution, commit, create-pr, close-slice, breakdown

## Interfaces and Responsibilities

- `make install` registers the managed packaged skill set after syncing shared packaged dependencies and references.
- `make uninstall` removes only the managed packaged skill names currently installed.
- `make install-packaged` registers the managed packaged skill set.
- `make uninstall-packaged` removes only the managed packaged skill names currently installed.
- `scripts/sync_shared_skill_runtime.py` copies shared runtime modules into packaged skills that import them before packaged installation runs.
- `manage_planning.py` reads `planning.json` for `planning_dir`.
- `manage_execution.py` reads `execution.json` for `slice_dir`, `preferred_workflow`, and `auto_start_implementation`.
- `manage_execution.py`, `commit`, `create-pr`, and `close-slice` read `conventions.json` for naming and issue-link behavior.

## Constraints and Tradeoffs

- Separate config files keep ownership clear but require discipline to avoid overlap.
- Plugin behavior is explicit rather than automatic, which improves safety but reduces convenience.
- Makefile-based installation is predictable but requires updates whenever the managed skill set changes.
- Packaged installs are the only supported workflow, so shared packaged runtime dependencies must be synchronized before registration.

## Validation Strategy

- Use repository tests that exercise config readers in planning, execution, breakdown, and close-slice flows.
- Review `README.md` and `AGENTS.md` whenever config semantics change.
- Verify packaged skills that import shared runtime support receive those synced runtime files before installation.
- Verify `make install-packaged` / `make uninstall-packaged` continue to match the managed packaged skill list.
- Verify `make install` / `make uninstall` behave as the default packaged entrypoints.

## PlantUML

```plantuml
@startuml
actor Maintainer
folder ".skills/" {
  file "planning.json"
  file "execution.json"
  file "conventions.json"
  folder "plugins/"
}
component Makefile
component "guide-planning" as Planning
component "guide-execution" as Execution
component commit
component "create-pr" as CreatePR
component breakdown
component "close-slice" as CloseSlice

Maintainer --> Makefile : install / uninstall
Planning --> "planning.json"
Execution --> "execution.json"
Execution --> "conventions.json"
commit --> "conventions.json"
CreatePR --> "conventions.json"
breakdown --> "planning.json"
CloseSlice --> "conventions.json"
CloseSlice --> "plugins/"
@enduml
```
