class OrderRepository:
    def __init__(self) -> None:
        self.orders: dict[str, str] = {}

    def save(self, order_id: str, authorization: str) -> None:
        self.orders[order_id] = authorization
