import { describe, expect, test, beforeEach, afterEach } from "bun:test";
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import { evaluateRepository, loadSkillDescriptions, frontmatterValue } from "../scripts/evals/routing";

const REPO_ROOT = path.resolve(__dirname, "..");

function makeTempDir(): string {
  return fs.mkdtempSync(path.join(os.tmpdir(), "sirius-test-routing-"));
}

function writeSkill(root: string, name: string, description: string): void {
  const skillFile = path.join(root, "skills", name, "SKILL.md");
  fs.mkdirSync(path.dirname(skillFile), { recursive: true });
  fs.writeFileSync(
    skillFile,
    `---\nname: ${name}\ndescription: ${description}\n---\n\n# ${name}\n`,
    "utf-8"
  );
}

function writeCase(root: string, name: string, data: Record<string, any>): void {
  const caseFile = path.join(root, "evals", "cases", `${name}.json`);
  fs.mkdirSync(path.dirname(caseFile), { recursive: true });
  fs.writeFileSync(caseFile, JSON.stringify(data, null, 2), "utf-8");
}

describe("routing", () => {
  let tmpDir: string;

  beforeEach(() => {
    tmpDir = makeTempDir();
  });

  afterEach(() => {
    if (fs.existsSync(tmpDir)) {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  test("frontmatterValue extracts keys correctly", () => {
    const doc = '---\nname: my-skill\ndescription: "A helpful skill for testing."\n---\n';
    expect(frontmatterValue(doc, "name")).toBe("my-skill");
    expect(frontmatterValue(doc, "description")).toBe("A helpful skill for testing.");
    expect(frontmatterValue(doc, "missing")).toBeNull();
  });

  test("evaluator checks positive and owned negative routes", () => {
    writeSkill(tmpDir, "behavior", "Recover observable commands and API behavior.");
    writeSkill(tmpDir, "architecture", "Recover modules and architecture dependencies.");
    writeCase(tmpDir, "behavior", {
      skill_name: "behavior",
      trigger: {
        positive: [{ prompt: "Recover the observable API behavior", top_k: 1 }],
        negative: [
          {
            prompt: "Map the architecture modules and dependencies",
            owner: "architecture",
          },
        ],
      },
      evals: [
        {
          id: "recover-api",
          prompt: "Recover this API's behavior.",
          expected_output: "An evidence-backed behavior model.",
          expectations: ["Observable behavior is separated from inference."],
        },
      ],
    });

    const report = evaluateRepository(tmpDir);

    expect(report.errors).toEqual([]);
    expect(report.routingChecks).toBe(2);
    expect(report.routingPassed).toBe(2);
  });

  test("evaluator rejects unknown negative owner", () => {
    writeSkill(tmpDir, "behavior", "Recover observable behavior.");
    writeCase(tmpDir, "behavior", {
      skill_name: "behavior",
      trigger: {
        positive: [],
        negative: [{ prompt: "Commit this change", owner: "missing-skill" }],
      },
      evals: [],
    });

    const report = evaluateRepository(tmpDir);

    expect(
      report.errors.some((err) =>
        err.includes("negative trigger declares unknown owner")
      )
    ).toBe(true);
  });

  test("evaluator flags description collisions", () => {
    writeSkill(
      tmpDir,
      "skill-one",
      "Deploy application containers to cluster environments using automated pipelines."
    );
    writeSkill(
      tmpDir,
      "skill-two",
      "Deploy application containers to cluster environments using automated pipelines."
    );

    const report = evaluateRepository(tmpDir);

    expect(
      report.errors.some((err) => err.includes("description collision: skill-one and skill-two"))
    ).toBe(true);
  });

  test("evaluator runs against real repository with 103/103 passing checks", () => {
    const report = evaluateRepository(REPO_ROOT);

    expect(report.errors).toEqual([]);
    expect(report.skillCount).toBe(18);
    expect(report.caseFiles).toBe(18);
    expect(report.routingChecks).toBe(103);
    expect(report.routingPassed).toBe(103);
    expect(report.rankOneRate).toBeGreaterThanOrEqual(0.95);
  });
});
