# Order Domain Model

This is the canonical vocabulary and rule summary for the order domain.

## Concepts

- **Order** has an `order_id` and an `OrderStatus`.
- **OrderStatus** is one of `NEW`, `SUBMITTED`, `SHIPPED`, or `CANCELLED`.

## Lifecycle

- A new order may be submitted.
- A submitted order may be shipped or cancelled.
