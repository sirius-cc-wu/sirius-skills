from src.payment import PaymentClient
from src.storage import OrderRepository


class OrderService:
    def __init__(
        self, payments: PaymentClient, repository: OrderRepository
    ) -> None:
        self._payments = payments
        self._repository = repository

    def place(self, order_id: str, amount: int) -> None:
        authorization = self._payments.authorize(order_id, amount)
        self._repository.save(order_id, authorization)
