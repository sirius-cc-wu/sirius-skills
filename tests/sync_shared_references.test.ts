import { describe, expect, test } from "bun:test";
import { spawnSync } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const root = resolve(__dirname, "..");

describe("sync_shared_references.ts", () => {
  test("runs without arguments and outputs status", () => {
    const result = spawnSync("bun", ["scripts/sync_shared_references.ts"], {
      cwd: root,
      encoding: "utf-8",
    });

    expect(result.status).toBe(0);
    expect(result.stdout).toContain("skills/behavior-preserving-refactoring/references/config-surface-governance.md");
  });

  test("rejects unexpected arguments", () => {
    const result = spawnSync("bun", ["scripts/sync_shared_references.ts", "--unexpected"], {
      cwd: root,
      encoding: "utf-8",
    });

    expect(result.status).toBe(2);
    expect(result.stderr).toContain("sync-shared-references does not accept arguments.");
  });
});
