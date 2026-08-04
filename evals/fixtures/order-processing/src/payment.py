class PaymentClient:
    def authorize(self, order_id: str, amount: int) -> str:
        return f"authorized:{order_id}:{amount}"
