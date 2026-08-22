# Configuration Surface Governance

Read this reference when planning, reviewing, or refactoring work that touches
configuration, startup, compatibility boundaries, environment injection, or
test harness inputs.

## Goal

Keep configuration ownership explicit and minimal so the system does not grow
parallel control planes for the same value.

## Governing rules

1. Prefer typed owners first.
   - Reuse existing typed structs, parameters, builders, or owned configuration
     objects before introducing environment variables, CLI flags, globals, or
     singleton reads.
2. Keep one control plane per value.
   - If a value already has an owned typed carrier, do not add a second
     configuration path unless the design records why it is required.
3. Push raw inputs to the outermost boundary.
   - Environment variables, CLI flags, files, and other process-global inputs
     belong only at the external compatibility boundary and should be converted
     immediately into typed internal state.
4. Preserve established ownership by default.
   - New components and change sets should use the documented configuration
     model unless they record and justify an explicit compatibility boundary.
5. Record rejected alternatives.
   - When a new configuration surface is introduced, explain why extending the
     existing typed owner was not sufficient.

## Questions to answer

1. Which component, configuration object, or type owns each externally supplied
   value?
2. Does the proposal add another way to configure a value that already exists?
3. Can the raw input be parsed once at the edge and passed around as typed
   state instead of being re-read globally?
4. Does the existing design or configuration contract already answer this?
5. If a second control plane is unavoidable, who owns the translation and how
   is drift prevented?

## Red flags

- environment variables added inside product logic instead of only at the
  compatibility edge
- startup code, tests, and runtime each inventing their own override path
- existing design docs describe typed ownership, but a new component adds raw
  process-global reads
- "temporary" shims with no exit criteria or owning boundary
