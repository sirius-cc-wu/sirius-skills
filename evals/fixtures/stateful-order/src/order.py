from enum import Enum
from typing import Protocol


class OrderStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class FulfillmentPort(Protocol):
    def schedule(self, order_id: str) -> None: ...


class Order:
    def __init__(self, order_id: str, fulfillment: FulfillmentPort) -> None:
        self.order_id = order_id
        self.status = OrderStatus.DRAFT
        self._fulfillment = fulfillment

    def submit(self) -> None:
        if self.status is not OrderStatus.DRAFT:
            raise ValueError("only draft orders can be submitted")
        self.status = OrderStatus.SUBMITTED

    def ship(self) -> None:
        if self.status is not OrderStatus.SUBMITTED:
            raise ValueError("only submitted orders can be shipped")
        self._fulfillment.schedule(self.order_id)
        self.status = OrderStatus.SHIPPED

    def cancel(self) -> None:
        if self.status is OrderStatus.SHIPPED:
            raise ValueError("shipped orders cannot be cancelled")
        self.status = OrderStatus.CANCELLED
