import { describe, expect, test } from "bun:test";
import { Order } from "../src/domain";
import { OrderCheckoutService } from "../src/service";

describe("OrderCheckoutService", () => {
  test("calculates subtotal correctly on order", () => {
    const order = new Order("ord-1", [
      { id: "i1", name: "Widget", unitPriceCents: 1000, quantity: 2 },
      { id: "i2", name: "Gadget", unitPriceCents: 500, quantity: 1 },
    ]);
    expect(order.subtotalCents()).toBe(2500);
  });

  test("calculates total with tax directly via calculateTotalWithTax", () => {
    const service = new OrderCheckoutService();
    const order = new Order(
      "ord-tax",
      [{ id: "i1", name: "Widget", unitPriceCents: 1000, quantity: 1 }],
      "SIRIUS10"
    );
    // subtotal = 1000, discount = 100 => 900, tax 10% = 90 => 990
    const total = service.calculateTotalWithTax(order, 0.1);
    expect(total).toBe(990);
  });

  test("calculates total with tax and discount correctly", () => {
    const service = new OrderCheckoutService();
    const order = new Order(
      "ord-2",
      [{ id: "i1", name: "Widget", unitPriceCents: 1000, quantity: 1 }],
      "SIRIUS10"
    );
    // subtotal = 1000, discount = 100 => 900, tax 10% = 90 => 990
    const result = service.processCheckout(order, 0.1);
    expect(result.totalCents).toBe(990);
  });
});
