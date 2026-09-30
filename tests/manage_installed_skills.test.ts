import { describe, expect, test, beforeEach, afterEach } from "bun:test";
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import {
  readRetirements,
  selectRetiredSkills,
  recordInstalled,
  recordNames,
  forgetNames,
  forgetRetired,
  linkProfile,
  unlinkProfile,
  unlinkRetired,
  removeLockedProfile,
  main,
} from "../scripts/manage_installed_skills";

const REPO_ROOT = path.resolve(__dirname, "..");

function makeTempDir(): string {
  return fs.mkdtempSync(path.join(os.tmpdir(), "sirius-test-manage-"));
}

function writeLedger(filePath: string): void {
  fs.writeFileSync(
    filePath,
    "# skill<TAB>retired revision\n" +
      "design\t36f7542d39225e1160c3a4b36c76dfd067fd0281\n" +
      "old-workflow\t3b78f0001ca391e321f52f5ebbd8043c7762f2ac\n",
    "utf-8"
  );
}

describe("manage_installed_skills", () => {
  let tmpDir: string;

  beforeEach(() => {
    tmpDir = makeTempDir();
  });

  afterEach(() => {
    if (fs.existsSync(tmpDir)) {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  test("selectRetiredSkills removes only owned names by default", () => {
    const ledgerPath = path.join(tmpDir, "retired-skills.tsv");
    const statePath = path.join(tmpDir, "managed-skills.txt");
    writeLedger(ledgerPath);
    fs.writeFileSync(statePath, "old-workflow\ncurrent-skill\n", "utf-8");

    const installedJson = JSON.stringify([
      { name: "design" },
      { name: "old-workflow" },
      { name: "external:skill" },
      { name: "unrelated" },
    ]);

    const { selected, unowned } = selectRetiredSkills(installedJson, {
      ledgerPath,
      statePath,
    });

    expect(selected).toEqual(["old-workflow"]);
    expect(unowned).toEqual(["design"]);
  });

  test("selectRetiredSkills can include unowned legacy candidates", () => {
    const ledgerPath = path.join(tmpDir, "retired-skills.tsv");
    writeLedger(ledgerPath);

    const { selected, unowned } = selectRetiredSkills(
      JSON.stringify([{ name: "design" }, { name: "old-workflow" }]),
      {
        ledgerPath,
        statePath: path.join(tmpDir, "missing-state.txt"),
        includeUnowned: true,
      }
    );

    expect(selected).toEqual(["design", "old-workflow"]);
    expect(unowned).toEqual([]);
  });

  test("recordInstalled and removal maintain host-local ownership", () => {
    const statePath = path.join(tmpDir, "state", "managed-skills.txt");
    const profilePath = path.join(tmpDir, "profile.txt");
    fs.writeFileSync(profilePath, "# selected profile\ncurrent-skill\nexample-skill\n", "utf-8");

    recordInstalled(profilePath, statePath);
    recordNames(["another-skill"], statePath);
    forgetNames(["example-skill"], statePath);

    expect(fs.readFileSync(statePath, "utf-8")).toBe("another-skill\ncurrent-skill\n");
  });

  test("forgetRetired cleans stale ownership entries", () => {
    const ledgerPath = path.join(tmpDir, "retired-skills.tsv");
    const statePath = path.join(tmpDir, "managed-skills.txt");
    writeLedger(ledgerPath);
    fs.writeFileSync(statePath, "current-skill\ndesign\nold-workflow\n", "utf-8");

    forgetRetired(ledgerPath, statePath);

    expect(fs.readFileSync(statePath, "utf-8")).toBe("current-skill\n");
  });

  test("linkProfile exposes canonical skills and is idempotent", () => {
    const profilePath = path.join(tmpDir, "profile.txt");
    const sourceDir = path.join(tmpDir, ".agents", "skills");
    const targetDir = path.join(tmpDir, ".gemini", "config", "skills");
    fs.writeFileSync(profilePath, "current-skill\nexample-skill\n", "utf-8");
    for (const name of ["current-skill", "example-skill"]) {
      fs.mkdirSync(path.join(sourceDir, name), { recursive: true });
    }
    fs.mkdirSync(targetDir, { recursive: true });
    fs.mkdirSync(path.join(targetDir, "external-skill"), { recursive: true });

    linkProfile(profilePath, { sourceDir, targetDir });
    linkProfile(profilePath, { sourceDir, targetDir });

    const currentSkillTarget = path.join(targetDir, "current-skill");
    expect(fs.lstatSync(currentSkillTarget).isSymbolicLink()).toBe(true);
    expect(fs.realpathSync(currentSkillTarget)).toBe(
      fs.realpathSync(path.join(sourceDir, "current-skill"))
    );
    expect(fs.realpathSync(path.join(targetDir, "example-skill"))).toBe(
      fs.realpathSync(path.join(sourceDir, "example-skill"))
    );
    expect(fs.statSync(path.join(targetDir, "external-skill")).isDirectory()).toBe(true);
  });

  test("linkProfile rejects conflicts before creating any links", () => {
    const profilePath = path.join(tmpDir, "profile.txt");
    const sourceDir = path.join(tmpDir, ".agents", "skills");
    const targetDir = path.join(tmpDir, ".gemini", "config", "skills");
    fs.writeFileSync(profilePath, "current-skill\nexample-skill\n", "utf-8");
    for (const name of ["current-skill", "example-skill"]) {
      fs.mkdirSync(path.join(sourceDir, name), { recursive: true });
    }
    fs.mkdirSync(path.join(targetDir, "example-skill"), { recursive: true });

    expect(() => {
      linkProfile(profilePath, { sourceDir, targetDir });
    }).toThrow("refusing to replace");

    expect(fs.existsSync(path.join(targetDir, "current-skill"))).toBe(false);
    expect(fs.statSync(path.join(targetDir, "example-skill")).isDirectory()).toBe(true);
  });

  test("unlinkProfile removes only links to expected canonical skills", () => {
    const profilePath = path.join(tmpDir, "profile.txt");
    const sourceDir = path.join(tmpDir, ".agents", "skills");
    const targetDir = path.join(tmpDir, ".gemini", "config", "skills");
    const foreignDir = path.join(tmpDir, "foreign");

    fs.writeFileSync(profilePath, "current-skill\nexample-skill\n", "utf-8");
    for (const name of ["current-skill", "example-skill"]) {
      fs.mkdirSync(path.join(sourceDir, name), { recursive: true });
    }
    fs.mkdirSync(targetDir, { recursive: true });
    fs.mkdirSync(foreignDir, { recursive: true });

    fs.symlinkSync(
      path.relative(targetDir, path.join(sourceDir, "current-skill")),
      path.join(targetDir, "current-skill"),
      "dir"
    );
    fs.symlinkSync(
      path.relative(targetDir, foreignDir),
      path.join(targetDir, "example-skill"),
      "dir"
    );

    unlinkProfile(profilePath, { sourceDir, targetDir });

    expect(fs.existsSync(path.join(targetDir, "current-skill"))).toBe(false);
    expect(fs.lstatSync(path.join(targetDir, "example-skill")).isSymbolicLink()).toBe(true);
    expect(fs.realpathSync(path.join(targetDir, "example-skill"))).toBe(
      fs.realpathSync(foreignDir)
    );
  });

  test("unlinkRetired links respect ownership by default", () => {
    const ledgerPath = path.join(tmpDir, "retired-skills.tsv");
    const statePath = path.join(tmpDir, "managed-skills.txt");
    const sourceDir = path.join(tmpDir, ".agents", "skills");
    const targetDir = path.join(tmpDir, ".gemini", "config", "skills");
    writeLedger(ledgerPath);
    fs.writeFileSync(statePath, "old-workflow\n", "utf-8");
    fs.mkdirSync(sourceDir, { recursive: true });
    fs.mkdirSync(targetDir, { recursive: true });

    for (const name of ["design", "old-workflow"]) {
      fs.symlinkSync(
        path.join(sourceDir, name),
        path.join(targetDir, name),
        "dir"
      );
    }

    unlinkRetired(ledgerPath, {
      statePath,
      sourceDir,
      targetDir,
    });

    expect(fs.lstatSync(path.join(targetDir, "design")).isSymbolicLink()).toBe(true);
    expect(fs.existsSync(path.join(targetDir, "old-workflow"))).toBe(false);

    unlinkRetired(ledgerPath, {
      statePath,
      sourceDir,
      targetDir,
      includeUnowned: true,
    });

    expect(fs.existsSync(path.join(targetDir, "design"))).toBe(false);
  });

  test("removeLockedProfile removes only the expected source", () => {
    const profilePath = path.join(tmpDir, "external-profile.txt");
    const lockPath = path.join(tmpDir, "skills-lock.json");
    const skillsDir = path.join(tmpDir, ".agents/skills");
    fs.writeFileSync(profilePath, "interview-me\nidea-refine\n", "utf-8");
    fs.writeFileSync(
      lockPath,
      JSON.stringify(
        {
          version: 1,
          skills: {
            "interview-me": { source: "addyosmani/agent-skills" },
            "idea-refine": { source: "another/source" },
            unrelated: { source: "another/source" },
          },
        },
        null,
        2
      ),
      "utf-8"
    );

    for (const name of ["interview-me", "idea-refine", "unrelated"]) {
      fs.mkdirSync(path.join(skillsDir, name), { recursive: true });
      fs.writeFileSync(path.join(skillsDir, name, "SKILL.md"), name, "utf-8");
    }

    removeLockedProfile(profilePath, {
      lockPath,
      skillsDir,
      source: "addyosmani/agent-skills",
    });

    expect(fs.existsSync(path.join(skillsDir, "interview-me"))).toBe(false);
    expect(fs.readFileSync(path.join(skillsDir, "idea-refine", "SKILL.md"), "utf-8")).toBe(
      "idea-refine"
    );
    expect(fs.readFileSync(path.join(skillsDir, "unrelated", "SKILL.md"), "utf-8")).toBe(
      "unrelated"
    );
    const remaining = JSON.parse(fs.readFileSync(lockPath, "utf-8")).skills;
    expect(Object.keys(remaining).sort()).toEqual(["idea-refine", "unrelated"]);
  });

  test("removeLockedProfile validates all targets before removal", () => {
    const profilePath = path.join(tmpDir, "external-profile.txt");
    const lockPath = path.join(tmpDir, "skills-lock.json");
    const skillsDir = path.join(tmpDir, ".agents/skills");
    fs.writeFileSync(profilePath, "interview-me\nidea-refine\n", "utf-8");
    fs.writeFileSync(
      lockPath,
      JSON.stringify(
        {
          version: 1,
          skills: {
            "interview-me": { source: "addyosmani/agent-skills" },
            "idea-refine": { source: "addyosmani/agent-skills" },
          },
        },
        null,
        2
      ),
      "utf-8"
    );

    fs.mkdirSync(path.join(skillsDir, "interview-me"), { recursive: true });
    fs.mkdirSync(skillsDir, { recursive: true });
    fs.writeFileSync(path.join(skillsDir, "idea-refine"), "conflict", "utf-8");

    expect(() => {
      removeLockedProfile(profilePath, {
        lockPath,
        skillsDir,
        source: "addyosmani/agent-skills",
      });
    }).toThrow("not a directory or symlink");

    expect(fs.statSync(path.join(skillsDir, "interview-me")).isDirectory()).toBe(true);
    expect(fs.statSync(path.join(skillsDir, "idea-refine")).isFile()).toBe(true);
  });

  test("retirement ledger rejects malformed entries and duplicate names", () => {
    const ledgerPath = path.join(tmpDir, "retired-skills.tsv");

    fs.writeFileSync(ledgerPath, "Bad_Name\t36f7542d39225e1160c3a4b36c76dfd067fd0281\n", "utf-8");
    expect(() => readRetirements(ledgerPath)).toThrow("retired-skills.tsv:1");

    fs.writeFileSync(ledgerPath, "design\tnot-a-revision\n", "utf-8");
    expect(() => readRetirements(ledgerPath)).toThrow("retired-skills.tsv:1");

    fs.writeFileSync(
      ledgerPath,
      "design\t36f7542d39225e1160c3a4b36c76dfd067fd0281\n" +
        "design\t3b78f0001ca391e321f52f5ebbd8043c7762f2ac\n",
      "utf-8"
    );
    expect(() => readRetirements(ledgerPath)).toThrow("duplicate retired skill design");
  });

  test("repository retirement ledger is disjoint from active skills", () => {
    const retirements = readRetirements(path.join(REPO_ROOT, "catalog/retired-skills.tsv"));
    const retiredNames = new Set(retirements.map((e) => e.name));
    const skillEntries = fs.readdirSync(path.join(REPO_ROOT, "skills"));
    const activeNames = new Set(
      skillEntries.filter((name) =>
        fs.existsSync(path.join(REPO_ROOT, "skills", name, "SKILL.md"))
      )
    );

    expect(retirements.length).toBe(84);
    for (const name of activeNames) {
      expect(retiredNames.has(name)).toBe(false);
    }
  });

  test("CLI main handles link-profile and record-installed", async () => {
    const profilePath = path.join(tmpDir, "profile.txt");
    const statePath = path.join(tmpDir, "state.txt");
    const sourceDir = path.join(tmpDir, "src-skills");
    const targetDir = path.join(tmpDir, "tgt-skills");

    fs.writeFileSync(profilePath, "test-skill\n", "utf-8");
    fs.mkdirSync(path.join(sourceDir, "test-skill"), { recursive: true });

    const code1 = await main([
      "link-profile",
      `--profile=${profilePath}`,
      `--source-dir=${sourceDir}`,
      `--target-dir=${targetDir}`,
    ]);
    expect(code1).toBe(0);
    expect(fs.lstatSync(path.join(targetDir, "test-skill")).isSymbolicLink()).toBe(true);

    const code2 = await main([
      "record-installed",
      `--profile=${profilePath}`,
      `--state=${statePath}`,
    ]);
    expect(code2).toBe(0);
    expect(fs.readFileSync(statePath, "utf-8")).toBe("test-skill\n");
  });
});
