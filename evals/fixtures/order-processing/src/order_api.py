from src.order_service import OrderService


def place_order(service: OrderService, order_id: str, amount: int) -> str:
    service.place(order_id, amount)
    return order_id
