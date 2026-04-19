# System Design: Installation and Configuration

## Overview

Installation and configuration form the repository integration layer. The
`Makefile` now exposes both a source-linked local install path and a packaged
compatibility path, while the `.skills/` directory provides separate
configuration surfaces for planning layout, execution layout, and naming
conventions. Project-local extensions live in `.skills/plugins/` and are only
used when a specific skill explicitly opts in.

## Key Components

- **Managed install entrypoint**: `Makefile`
- **Local install helper**: `scripts/install_local_skills.py`
- **Planning layout config**: `.skills/planning.json`
- **Execution layout config**: `.skills/execution.json`
- **Conventions config**: `.skills/conventions.json`
- **Project-local extensions**: `.skills/plugins/`
- **Consumer skills**: guide-planning, guide-execution, commit, create-pr, close-slice, breakdown

## Interfaces and Responsibilities

- `make install-local` symlinks the managed skill set into a selected skill home.
- `make uninstall-local` removes only the managed local symlinks created for the managed skill names.
- `make install-packaged` registers the managed packaged skill set.
- `make uninstall-packaged` removes only the managed packaged skill names currently installed.
- `make install` and `make uninstall` remain compatibility aliases to the packaged path in the current rollout.
- `manage_planning.py` reads `planning.json` for `planning_dir`.
- `manage_execution.py` reads `execution.json` for `slice_dir`, `preferred_workflow`, and `auto_start_implementation`.
- `manage_execution.py`, `commit`, `create-pr`, and `close-slice` read `conventions.json` for naming and issue-link behavior.

## Constraints and Tradeoffs

- Separate config files keep ownership clear but require discipline to avoid overlap.
- Plugin behavior is explicit rather than automatic, which improves safety but reduces convenience.
- Makefile-based installation is predictable but requires updates whenever the managed skill set changes.
- The current rollout keeps local and packaged paths on different target names, but only the local path has been split explicitly so far.

## Validation Strategy

- Use repository tests that exercise config readers in planning, execution, breakdown, and close-slice flows.
- Review `README.md` and `AGENTS.md` whenever config semantics change.
- Verify `make install-local` / `make uninstall-local` match the managed skill list for source-linked installs.
- Verify `make install-packaged` / `make uninstall-packaged` continue to match the managed packaged skill list.
- Verify `make install` / `make uninstall` still behave as packaged compatibility aliases.

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
