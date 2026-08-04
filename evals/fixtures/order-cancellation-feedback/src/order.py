from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    NEW = "new"
    SUBMITTED = "submitted"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


@dataclass
class Order:
    order_id: str
    status: OrderStatus = OrderStatus.NEW
    cancellation_reason: str | None = None

    def submit(self) -> None:
        if self.status is not OrderStatus.NEW:
            raise ValueError("only new orders can be submitted")
        self.status = OrderStatus.SUBMITTED

    def ship(self) -> None:
        if self.status is not OrderStatus.SUBMITTED:
            raise ValueError("only submitted orders can be shipped")
        self.status = OrderStatus.SHIPPED

    def cancel(self) -> None:
        self.status = OrderStatus.CANCELLED
