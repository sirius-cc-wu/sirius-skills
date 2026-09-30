# Synthetic Fixture: PR Scope Mismatch

This fixture simulates a repository with a submitted pull request (PR #185) that suffers from severe scope creep.

## Motivating Issue (#180)
- **Problem**: Query cache entries are not pruned on timeout, leading to gradual memory growth during peak load.
- **Required Fix**: Evict expired cache entries when lookup detects timestamp expiration.

## Submitted PR (#185)
- **Delivered Changes**:
  1. `src/cache.ts`: Minimal 3-line expiration check and eviction.
  2. `src/event_bus.ts`: An unrequested 200-line asynchronous reactive event-bus subsystem.
  3. `src/plugin_manager.ts`: An unrequested dynamic plugin lifecycle manager.
- **Scope Creep**:
  The developer used a minor cache-leak bugfix to introduce an unrequested, speculative plugin and event-bus architecture into the core repository.
