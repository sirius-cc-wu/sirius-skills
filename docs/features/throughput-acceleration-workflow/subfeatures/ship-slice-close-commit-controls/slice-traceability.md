# Slice Traceability

Use this file to map repo story IDs to execution slices without moving story
ownership outside repository planning artifacts.

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TAW-02 | L | Safely derive the delegated run's owned file set for formatting and commit staging | I1 | scc-owned-change-set | owned-file tracking, formatter scope, spillover/conflict handling | taw-ship-slice-loop | scc-owned-change-set | Establishes the safety contract before terminal automation mutates closure or Git state. |
| TAW-02 | L | Optionally automate formatting, slice closure, and owned-file commit | I2 | scc-terminal-automation | terminal controls, close delegation, owned-file commit | scc-owned-change-set, taw-ship-backlog-integration |  | Reuses the owned-change-set contract and existing close/commit owners instead of reimplementing them inside `ship-slice`. |
