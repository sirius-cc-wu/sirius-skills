# Original example: checking out a reserved unit

Assumptions for this example: a staff member serves an already identified borrower; each checkout concerns one individually tracked unit; the unit has a reservation for that borrower; the agreed due date has been established by the applicable policy. These are example assumptions, not universal loan rules.

## Selected black-box events

The staff member sends `checkOut(reservationId)` to the lending system. On success, the system returns a loan reference and due date. A separate alternate path specifies what happens if the reservation has expired or the unit cannot be handed over. Internal repository and policy calls do not belong in this SSD.

## Contract

**Operation:** `checkOut(reservationId: ReservationId)`.

**Cross-reference:** Borrow Equipment, reserved-unit success path.

**Preconditions:** An authorized staff session exists; this successful-path contract assumes an active reservation `r` for borrower `b` and unit `u`, with an agreed due date. The surrounding scenario is responsible for specifying validation of those facts.

**Postconditions:**

- A `Loan` instance `l` was created.
- `l` was linked to `b` as its borrower and to `u` as its borrowed unit.
- `l.startedAt` was set to the recorded checkout time.
- `l.dueAt` was set to the due date established for `r`.
- `r.status` was changed to fulfilled, and `r` was linked to `l`.

If availability is derived from active loans, do not also invent an independently mutable `available` flag. If the domain explicitly stores status, include its required change and consistency rule.

## Review questions

- Can the new loan be found from the borrower and unit in the conceptual model?
- Is fulfillment different from deleting the reservation? Must history remain?
- Is due-date selection defined, or has the contract smuggled in an unstated rule?
- What externally visible result follows rejection? Does it leave no new loan?
- Could two concurrent requests violate the one-active-loan rule? State the required invariant; assign the mechanism during design.

The example demonstrates the contract technique in chapter 11, especially §§11.4–11.8, supplied PDF pp. 291–298. Names and behavior are original; the concurrency prompt is an implementation-oriented extension.
