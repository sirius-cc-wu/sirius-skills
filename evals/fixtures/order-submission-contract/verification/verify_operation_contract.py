from __future__ import annotations

import re
from pathlib import Path


feature = Path("docs/order-submission.md").read_text(encoding="utf-8")
marker = "## Contract: submitOrder(orderId)"
if marker not in feature:
    raise SystemExit("missing operation contract for submitOrder(orderId)")

if sum(line.strip() == "---" for line in feature.splitlines()) != 2:
    raise SystemExit("the aggregate must retain exactly one frontmatter block")

contract = feature.split(marker, 1)[1]
lowered = contract.lower()

for heading in ("Effect in Plain Language", "Preconditions", "Postconditions"):
    if not re.search(rf"^###{{1,2}} {re.escape(heading)}$", contract, re.MULTILINE):
        raise SystemExit(f"missing contract heading: {heading}")

for concept in (
    "Order",
    "DRAFT",
    "SUBMITTED",
    "OrderLine",
    "PaymentAuthorization",
    "InventoryReservation",
    "OrderSubmitted",
    "Shipment",
):
    if concept not in contract:
        raise SystemExit(f"missing contract concept: {concept}")

checks = {
    "order state change": r"Order.{0,80}(?:became|becomes|changed).{0,40}SUBMITTED",
    "payment authorization creation": r"PaymentAuthorization.{0,80}(?:created|was created)",
    "payment association": r"PaymentAuthorization.{0,120}associated.{0,60}Order",
    "reservation per line": r"InventoryReservation.{0,120}(?:each|every).{0,60}OrderLine",
    "event recording": r"OrderSubmitted.{0,100}(?:recorded|was recorded)",
    "no shipment": r"(?:no|not).{0,40}Shipment.{0,60}created|Shipment.{0,60}(?:not|no).{0,30}created",
}
for name, pattern in checks.items():
    if not re.search(pattern, contract, re.IGNORECASE | re.DOTALL):
        raise SystemExit(f"missing declarative postcondition: {name}")

for implementation_term in (
    "controller",
    "database",
    "repository",
    "sql",
    "OrderService",
):
    if implementation_term.lower() in lowered:
        raise SystemExit(f"contract contains implementation detail: {implementation_term}")
