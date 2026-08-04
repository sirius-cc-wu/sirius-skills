from collections.abc import Callable

from src.order import Order, OrderStatus


def expect_rejection(action: Callable[[], None]) -> None:
    try:
        action()
    except Exception:
        return
    raise AssertionError("the operation should have been rejected")


cancelled = Order("cancelled")
cancelled.submit()
cancelled.cancel("Customer changed their mind")
assert cancelled.status is OrderStatus.CANCELLED
assert cancelled.cancellation_reason == "Customer changed their mind"

for invalid_reason in ("", "   "):
    invalid = Order(f"invalid-{invalid_reason!r}")
    invalid.submit()
    expect_rejection(lambda order=invalid, reason=invalid_reason: order.cancel(reason))
    assert invalid.status is OrderStatus.SUBMITTED
    assert invalid.cancellation_reason is None

shipped = Order("shipped")
shipped.submit()
shipped.ship()
expect_rejection(lambda: shipped.cancel("No longer needed"))
assert shipped.status is OrderStatus.SHIPPED
assert shipped.cancellation_reason is None
