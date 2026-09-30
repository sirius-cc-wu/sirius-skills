import { describe, expect, test } from "bun:test";
import * as fs from "node:fs";
import * as path from "node:path";

const REPO_ROOT = path.resolve(__dirname, "..");

function read(relPath: string): string {
  return fs.readFileSync(path.join(REPO_ROOT, relPath), "utf-8");
}

describe("client discovery handoffs", () => {
  test("client_to_code track routes retired capabilities to active owners", () => {
    const track = read("catalog/tracks/client-to-code.md");

    for (const name of [
      "stakeholder-requirements-elicitation",
      "requirements-synthesis-validation",
      "implementation-slice-briefing",
    ]) {
      expect(track).toContain(name);
    }

    const normalizedTrack = track.replace(/\s+/g, " ");
    expect(normalizedTrack).toContain("are retired");
    expect(normalizedTrack).toContain("responsible external process");

    const skillLinks = [
      "../../skills/assess-development-input/SKILL.md",
      "../../skills/vision/SKILL.md",
      "../../skills/use-case-modeling/SKILL.md",
      "../../skills/specify-quality-constraints/SKILL.md",
      "../../skills/operation-contracts/SKILL.md",
    ];
    const positions = skillLinks.map((link) => track.indexOf(link));

    expect(positions).toEqual([...positions].sort((a, b) => a - b));
    expect(track).toContain("implementation-evolution.md");
  });

  test("assessment owns entry routing without replacing iteration coordination", () => {
    const assessment = read("skills/assess-development-input/SKILL.md").replace(/\s+/g, " ");
    const relationships = read("catalog/skill-relationships.md").replace(/\s+/g, " ");

    expect(assessment).toContain("This skill owns entry routing");
    expect(assessment).toContain("select one initial route without executing it");

    for (const group of [
      "Requirements Analysis",
      "System Analysis",
      "Software/System Design",
      "Detailed Design",
      "Implementation and Evolution",
      "Review",
      "Repository Workflow",
      "Integrate and ship",
      "Cross-cutting Support",
      "Iterative Coordination",
    ]) {
      expect(assessment).toContain(group);
    }

    const activeNames = new Set(
      read("skill-sets/all.txt")
        .split(/\r?\n/)
        .map((l) => l.trim())
        .filter((l) => l.length > 0 && !l.startsWith("#"))
    );

    const externalSkillSetsDir = path.join(REPO_ROOT, "catalog/external-skill-sets");
    const externalFiles = fs.readdirSync(externalSkillSetsDir).filter((f) => f.endsWith(".txt"));
    const externalNames = new Set<string>();
    for (const file of externalFiles) {
      const lines = fs.readFileSync(path.join(externalSkillSetsDir, file), "utf-8").split(/\r?\n/);
      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed && !trimmed.startsWith("#")) {
          externalNames.add(trimmed);
        }
      }
    }

    activeNames.delete("assess-development-input");
    const allExpected = new Set([...activeNames, ...externalNames]);
    for (const name of allExpected) {
      expect(assessment).toContain(`\`${name}\``);
    }

    expect(relationships).toContain("owns operational entry routing");
  });

  test("doubt driven addon challenges claims without claiming recovery", () => {
    const assessment = read("skills/assess-development-input/SKILL.md").replace(/\s+/g, " ");
    const relationships = read("catalog/skill-relationships.md").replace(/\s+/g, " ");
    const track = read("catalog/tracks/implementation-evolution.md").replace(/\s+/g, " ");

    expect(assessment).toContain("doubt-driven-development");
    expect(relationships).toContain("fresh-context adversarial review");
    expect(relationships).toContain("does not recover undocumented design");
    expect(track).toContain("instead of treating adversarial review as design recovery");
  });

  test("layout skill handles missing guidance without inventing taxonomy", () => {
    const layout = read("skills/design-repository-artifact-layout/SKILL.md");
    const normalizedLayout = layout.replace(/\s+/g, " ");

    expect(normalizedLayout).toContain("no explicit artifact guide or established convention");
    expect(normalizedLayout).toContain("absence of a layout guide");
    expect(normalizedLayout).toContain("generic");
  });
});
