export interface OrderItem {
  id: string;
  name: string;
  unitPriceCents: number;
  quantity: number;
}

export class Order {
  constructor(
    public readonly id: string,
    public readonly items: OrderItem[],
    public discountCode: string | null = null
  ) {}

  subtotalCents(): number {
    return this.items.reduce((sum, item) => sum + item.unitPriceCents * item.quantity, 0);
  }
}
