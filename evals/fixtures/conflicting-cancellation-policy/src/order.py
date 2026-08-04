from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    NEW = "new"
    SUBMITTED = "submitted"


@dataclass
class Order:
    order_id: str
    status: OrderStatus = OrderStatus.NEW

    def submit(self) -> None:
        if self.status is not OrderStatus.NEW:
            raise ValueError("only new orders can be submitted")
        self.status = OrderStatus.SUBMITTED
