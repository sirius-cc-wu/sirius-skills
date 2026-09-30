import { describe, expect, test } from "bun:test";
import { spawnSync } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const root = resolve(__dirname, "..");

describe("validate_skills.ts", () => {
  test("executes cleanly and validates repository skills", () => {
    const result = spawnSync("bun", ["scripts/validate_skills.ts"], {
      cwd: root,
      encoding: "utf-8",
    });

    expect(result.status).toBe(0);
    expect(result.stdout).toContain("Validated 17 skills across 5 profiles.");
    expect(result.stdout).toContain("Validated 11 external add-on skills");
    expect(result.stdout).toContain("Validated 84 retired skill tombstones.");
  });
});
