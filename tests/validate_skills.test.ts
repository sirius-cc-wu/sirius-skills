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

  test("skill descriptions with YAML indicator text are quoted", async () => {
    const fs = await import("node:fs");
    const path = await import("node:path");

    const skillsDir = path.join(root, "skills");
    const skillEntries = fs.readdirSync(skillsDir);
    for (const entry of skillEntries) {
      const skillFile = path.join(skillsDir, entry, "SKILL.md");
      if (!fs.existsSync(skillFile)) continue;
      const lines = fs.readFileSync(skillFile, "utf-8").split(/\r?\n/);
      const descLine = lines.find((l) => l.startsWith("description: "));
      expect(descLine).toBeDefined();
      const value = descLine!.slice("description: ".length);
      const isQuoted =
        value.length >= 2 &&
        value[0] === value[value.length - 1] &&
        (value[0] === '"' || value[0] === "'");
      if (value.includes(": ")) {
        expect(isQuoted).toBe(true);
      }
    }
  });
});

