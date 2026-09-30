export type Handler = (data: any) => Promise<void> | void;

export class ReactiveEventBus {
  private handlers = new Map<string, Set<Handler>>();

  subscribe(event: string, handler: Handler): () => void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);
    return () => this.handlers.get(event)?.delete(handler);
  }

  async publish(event: string, data: any): Promise<void> {
    const list = this.handlers.get(event);
    if (!list) return;
    for (const h of list) {
      await h(data);
    }
  }
}
