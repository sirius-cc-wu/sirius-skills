from src.order import Order, OrderStatus


def test_new_order_starts_new() -> None:
    order = Order("order-1")

    assert order.status is OrderStatus.NEW


def test_new_order_can_be_submitted() -> None:
    order = Order("order-1")

    order.submit()

    assert order.status is OrderStatus.SUBMITTED
