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

describe("quality-constraints", () => {
  test("quality_constraint skill preserves requirements and design boundary", () => {
    const skill = read("skills/specify-quality-constraints/SKILL.md").replace(/\s+/g, " ");

    const requiredPhrases = [
      "stimulus, operating condition, affected scope, required response, and measure",
      "candidate, approved, contested, inferred, and unknown",
      'type: "Supplementary Specification"',
      "design-software-architecture",
      "responsible external product or portfolio process",
      "External `idea-refine` can prepare a candidate direction, not approve it",
    ];

    for (const phrase of requiredPhrases) {
      expect(skill).toContain(phrase);
    }
  });

  test("quality_constraint skill is active and routable", () => {
    const name = "specify-quality-constraints";

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
