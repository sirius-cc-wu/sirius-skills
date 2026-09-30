# Synthetic Fixture: Refactor Boundary

This fixture represents a TypeScript/Bun project with green passing tests.

## Pressure
- `src/service.ts` owns an order pricing and discount calculation that violates information hiding by reaching into the order's internal items and discount rules.
- The cohesive calculation belongs on `src/domain.ts` (`Order`).

## Goal
- Move `calculateTotalWithTax` from `service.ts` to `Order` in `domain.ts`.
- Ensure all tests remain green and behavior is preserved.
