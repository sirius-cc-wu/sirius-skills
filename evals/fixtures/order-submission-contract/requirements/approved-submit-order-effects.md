# Approved Submit-Order Effects

Authority: approved by Product, Payments, and Fulfillment. These effects have
equal precedence and are mutually consistent.

When `submitOrder(orderId)` succeeds:

- the existing `Order` changes from `DRAFT` to `SUBMITTED`;
- one `PaymentAuthorization` is created and associated with the `Order`;
- one `InventoryReservation` is created for each `OrderLine` and associated
  with that line;
- one `OrderSubmitted` event is recorded for the `Order`; and
- no `Shipment` is created.

The operation assumes the identified order already exists in `DRAFT` state and
contains at least one `OrderLine`.
