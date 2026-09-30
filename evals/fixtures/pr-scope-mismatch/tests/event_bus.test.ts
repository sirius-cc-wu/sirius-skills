import { describe, expect, test } from "bun:test";
import { ReactiveEventBus } from "../src/event_bus";

describe("ReactiveEventBus", () => {
  test("publishes event to subscriber", async () => {
    const bus = new ReactiveEventBus();
    const received: any[] = [];
    bus.subscribe("msg", (data) => {
      received.push(data);
    });
    await bus.publish("msg", { text: "hello" });
    expect(received).toEqual([{ text: "hello" }]);
  });
});
