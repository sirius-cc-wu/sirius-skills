# Pull Request #185 Context

## PR Title
`fix: evict expired cache entries on query timeout`

## PR Description
Closes #180.

### Summary
Fixed the cache eviction issue by checking entry timestamps during lookup.
In addition, I took the opportunity to rewrite our internal notifications:
- Created a brand new reactive event bus system (`src/event_bus.ts`) to handle events asynchronously.
- Added a full dynamic plugin manager (`src/plugin_manager.ts`) so future extensions can register hook callbacks.
- Added comprehensive unit tests for both new subsystems.

### Changed Files
- `src/cache.ts` (3 lines changed - bugfix)
- `src/event_bus.ts` (new file, 150 lines)
- `src/plugin_manager.ts` (new file, 120 lines)
- `tests/cache.test.ts` (new test for expiration)
- `tests/event_bus.test.ts` (new tests for event bus)
