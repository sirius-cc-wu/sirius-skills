from src.order import Order, OrderStatus


def test_submitted_order_can_be_shipped() -> None:
    order = Order("order-1")

    order.submit()
    order.ship()

    assert order.status is OrderStatus.SHIPPED


def test_submitted_order_can_be_cancelled() -> None:
    order = Order("order-1")
    order.submit()

    order.cancel()

    assert order.status is OrderStatus.CANCELLED
