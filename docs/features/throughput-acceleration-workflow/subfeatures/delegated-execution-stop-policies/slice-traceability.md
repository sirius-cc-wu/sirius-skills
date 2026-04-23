# Slice Traceability

Use this file to map repo story IDs to execution slices without moving story
ownership outside repository planning artifacts.

| Story ID | Story Size | Story Summary | Increments | Planned Slice IDs | Slice Areas | Blocked By | Execution Slice IDs | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TAW-02 | M | Define the continuation-policy contract and readiness metadata for delegated execution | I1 | dsp-policy-contract | execution config, readiness metadata, delegate reporting | taw-ship-backlog-integration | dsp-policy-contract | Establishes the durable contract before behavior changes. |
| TAW-02 | M | Apply continuation policy to delegated review and commit boundaries | I2 | dsp-boundary-enforcement | delegated boundary handling, hard-stop preservation | dsp-policy-contract, scc-terminal-automation | dsp-boundary-enforcement | Depends on the sibling terminal-automation packet for commit-boundary continuation. |
