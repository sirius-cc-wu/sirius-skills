from src.invoice import round_invoice_total


def test_rounds_half_cent_up_for_invoice_total() -> None:
    assert round_invoice_total("2.675") == "2.68"
