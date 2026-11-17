---
name: maintain-verification-harness
description: "Periodic pass that keeps a project's verification harness and Glass Surface Map honest: parallel source readers per surface, one live session driving every surface, at most one PR of proven corrections. Use for /maintain-verification-harness, \"audit the surface map\", or when maintaining an existing verification harness."
---

# Maintain Verification Harness

A Glass Surface Map rots the moment the application changes. This skill is the upkeep loop for a harness and surface map created by `create-verification-harness` (or any project-local verification harness with a surface map). The unit of rigor is the surface, not every sentence: cover every surface file from source and exercise every surface live, without terminalizing every bullet.

## Outcomes

Pick one, and say which:

- **clean** — every surface got source and live coverage; nothing worth shipping. No branch, no PR.
- **changed** — one PR ships proven doc, harness, or surface map corrections.
- **blocked** — coverage could not finish or a proven fix could not ship safely. Say exactly what blocked it.

## Edit Scope

Only edit the verification harness and Glass Surface Map files (the surface map directory, harness scripts/configs, and any project-local `verify-*` skill). Never edit product code during a run: a behavior the map describes that the app no longer does is either doc drift (fix the map) or a product regression (report it, don't paper over it in docs).

## Pass

0. **Locate the target.** Find the verification harness and Glass Surface Map to maintain: `docs/ui/surface-map/` or `.agents/skills/verify-*/surfaces/` paired with its local harness script/config. Several candidates → ask which one; none → stop and point at `create-verification-harness` instead of inventing a target.

1. **Index hygiene.** Read the surface map index (`index/README.md` or `README.md`) and glob its sibling surface files. Fix missing, extra, duplicate, or dead entries. Lightweight; no generated inventory.

2. **Source wave.** One read-only subagent per surface file, launched concurrently. Each explains "how does this user-facing surface work?" from source, flags likely doc drift with citations, and returns one concise live-verification recipe. Children never drive the app and never edit files. Return shape: surface summary / source entry points / likely drift or none / one recipe.

3. **Reconcile.** Every surface file has a returned summary. Merge overlapping recipes into as few app states as practical. Spot-check cited drift; don't re-prove clean claims. Sweep recent churn for user-facing surfaces missing from the map — require a concrete source path before calling one missing.

4. **Live pass.** Required even when source looks clean. The coordinator owns all driving; follow the harness's own launch model — one long-lived instance driven serially for servers and UIs, or a fresh isolated session per drive for short-lived CLIs (the harness decides, not this skill). Exercise every surface at least once, and hold three invariants the whole pass, whatever the failure:
   1. Never drive an instance you haven't health-checked since it last did something surprising — run Doctor before the first drive, on each fresh session where sessions are the unit, and again after any failed drive; where Doctor can't see the failure (a wedged UI state on a healthy process), reset to a known state or relaunch rather than hoping.
   2. Evidence captured so far (screenshots, ARIA snapshots, transcripts, state proofs) survives every cleanup, checked at its named location on disk, not assumed.
   3. Nothing a drive started outlives that drive's usefulness — failed-iteration residue is cleaned whether the session is stuck, exited, or shared (for a shared instance, clean the residue, not the instance). Never kill by process name; kill only what the run started.

   A Doctor failure caused by harness or map drift is drift: fix it under Edit Scope and retry once — restart whatever the fix invalidated, nothing more — before calling the pass `blocked`. A surface that can't be reached is `verified-unreachable` only with the concrete prerequisite (auth, entitlement, OS, external state) and the route attempted; if the map omits that prerequisite, that's drift. Any harness fix from triage gets re-driven live before it ships. Final teardown happens after the last drive of the run — including those re-proofs — so nothing outlives the run (evidence stays, per the harness).

5. **Triage.** Wrong or missing user-POV description → doc drift, fix it. Working behavior the harness can't drive → harness gap, fix it (scripts executable, invocation documented). App behavior that's actually broken → product gap; record it for the user, keep it out of this PR.

6. **Ship or stop.** For `changed`: one PR of proven corrections, re-read every changed file first. For `clean` or `blocked`: no PR, report the outcome and the coverage honestly.

Keep concise run notes (surfaces covered, unreachable prerequisites, confirmed drift, outcome) in a scratch location; don't commit them.
