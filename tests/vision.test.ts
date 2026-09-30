import { describe, expect, test } from "bun:test";
import * as fs from "node:fs";
import * as path from "node:path";

const REPO_ROOT = path.resolve(__dirname, "..");

function read(relPath: string): string {
  return fs.readFileSync(path.join(REPO_ROOT, relPath), "utf-8");
}

function profileNames(relPath: string): Set<string> {
  const lines = read(relPath).split(/\r?\n/);
  return new Set(
    lines
      .map((l) => l.trim())
      .filter((l) => l.length > 0 && !l.startsWith("#"))
  );
}

describe("vision", () => {
  test("vision skill preserves evidence and approval boundaries", () => {
    const skill = read("skills/vision/SKILL.md").replace(/\s+/g, " ");

    const requiredPhrases = [
      "Treat history as evidence, not approval.",
      "existing vision",
      "accept-or-resist criteria",
      "External `idea-refine` owns candidate-direction exploration.",
      "business-case, feasibility, funding, and investment approval",
      'type: "Vision"',
      "Intended Users",
      "Scope",
      "Integration Boundary",
      "Boundary Cases",
      "Source revision",
    ];

    for (const phrase of requiredPhrases) {
      expect(skill).toContain(phrase);
    }
  });

  test("vision skill is active and routable", () => {
    const name = "vision";

    expect(profileNames("skill-sets/all.txt").has(name)).toBe(true);
    expect(profileNames("skill-sets/iterative-design.txt").has(name)).toBe(true);
    expect(profileNames("skill-sets/applying-uml-and-patterns.txt").has(name)).toBe(true);
    expect(profileNames("skill-sets/workflow.txt").has(name)).toBe(false);
    expect(profileNames("skill-sets/reverse-engineering.txt").has(name)).toBe(false);

    for (const relPath of [
      "skills/assess-development-input/SKILL.md",
      "catalog/skill-relationships.md",
    ]) {
      expect(read(relPath)).toContain(name);
    }
  });
});
