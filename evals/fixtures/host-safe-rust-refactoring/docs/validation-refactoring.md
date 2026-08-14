# Validation Refactoring Design

Status: active

## Current Local Seams

- The settings seam gives UDS, DoIP, and clients one immutable endpoint and
  socket description.
- The runtime-handle seam gives each service a focused start, shutdown, and
  wait API.

Focused tests for these seams pass.

## Known Gap

The current design does not assign ownership for composing the complete
validation run. It does not state which external scenario proves that the
parent host-safe outcome is complete.
