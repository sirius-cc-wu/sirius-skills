import { Order } from "./domain";

export class OrderCheckoutService {
  // Candidate calculation to move to Order: calculateTotalWithTax
  calculateTotalWithTax(order: Order, taxRate: number): number {
    const subtotal = order.subtotalCents();
    let discount = 0;
    if (order.discountCode === "SIRIUS10") {
      discount = Math.round(subtotal * 0.1);
    }
    const discounted = Math.max(0, subtotal - discount);
    const tax = Math.round(discounted * taxRate);
    return discounted + tax;
  }

  processCheckout(order: Order, taxRate: number): { orderId: string; totalCents: number } {
    const totalCents = this.calculateTotalWithTax(order, taxRate);
    return {
      orderId: order.id,
      totalCents,
    };
  }
}
