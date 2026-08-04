def round_invoice_total(amount: str) -> str:
    return f"{round(float(amount), 2):.2f}"
