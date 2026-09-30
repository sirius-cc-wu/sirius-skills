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

describe("audit-pr-scope", () => {
  test("audit_pr_scope skill preserves boundaries and structure", () => {
    const skill = read("skills/audit-pr-scope/SKILL.md").replace(/\s+/g, " ");

    const requiredPhrases = [
      "Audits whether a pull request's scope matches its motivating problem.",
      "Motivating Problem",
      "Over-engineering",
      "Under-engineering",
      "Slice A",
      "Slice B",
      "flowchart",
      "Maintains strict read-only boundaries.",
    ];

    for (const phrase of requiredPhrases) {
      expect(skill).toContain(phrase);
    }
  });

  test("audit_pr_scope skill is active and routable", () => {
    const name = "audit-pr-scope";

    expect(profileNames("skill-sets/all.txt").has(name)).toBe(true);
    expect(profileNames("skill-sets/workflow.txt").has(name)).toBe(true);
    expect(profileNames("skill-sets/iterative-design.txt").has(name)).toBe(false);
    expect(profileNames("skill-sets/applying-uml-and-patterns.txt").has(name)).toBe(false);
    expect(profileNames("skill-sets/reverse-engineering.txt").has(name)).toBe(false);
  });
});
