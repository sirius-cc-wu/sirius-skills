import { describe, expect, test } from "bun:test";
import { QueryCache } from "../src/cache";

describe("QueryCache", () => {
  test("evicts expired entry on lookup", async () => {
    const cache = new QueryCache<string>();
    cache.set("k1", "v1", 10);
    expect(cache.get("k1")).toBe("v1");
    await new Promise((r) => setTimeout(r, 20));
    expect(cache.get("k1")).toBeUndefined();
  });
});
