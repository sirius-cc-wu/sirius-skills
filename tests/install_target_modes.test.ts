import { describe, expect, test } from "bun:test";
import * as fs from "node:fs";
import * as path from "node:path";
import * as child_process from "node:child_process";

const REPO_ROOT = path.resolve(__dirname, "..");
const SYNC_REFERENCES = "scripts/sync_shared_references.ts";
const NPX_SKILLS = "npx --yes skills";
const PACKAGED_ADD = `${NPX_SKILLS} add "`;
const PACKAGED_REPO_SOURCE = `${PACKAGED_ADD}${REPO_ROOT}"`;
const SOURCE_SKILLS_DIR = path.join(REPO_ROOT, "skills");
const TARGET_PROJECT = "/tmp/sirius-say";
const ADDY_EXTERNAL_PROFILE = path.join(REPO_ROOT, "catalog/external-skill-sets/addy-osmani.txt");
const ADDY_SOURCE = "addyosmani/agent-skills@5a1b82d6445d1e2f0abeea1072851419a50c0e5c";
const EXTERNAL_SOURCES = [ADDY_SOURCE];
const ADDY_SKILLS = new Set([
  "interview-me",
  "idea-refine",
  "spec-driven-development",
  "doubt-driven-development",
  "test-driven-development",
  "browser-testing-with-devtools",
  "debugging-and-error-recovery",
  "code-review-and-quality",
  "code-simplification",
  "git-workflow-and-versioning",
  "documentation-and-adrs",
]);
const EXTERNAL_SKILLS = ADDY_SKILLS;
const PROFILE_NAMES = [
  "workflow",
  "iterative-design",
  "applying-uml-and-patterns",
  "reverse-engineering",
  "all",
];

function renderJust(target: string, ...args: string[]): string {
  const result = child_process.spawnSync("just", ["-n", target, ...args], {
    cwd: REPO_ROOT,
    encoding: "utf-8",
  });
  return (result.stdout || "") + (result.stderr || "");
}

function readProfile(name: string): Set<string> {
  const content = fs.readFileSync(path.join(REPO_ROOT, "skill-sets", `${name}.txt`), "utf-8");
  return new Set(
    content
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter((l) => l.length > 0 && !l.startsWith("#"))
  );
}

function readExternalProfile(p: string): Set<string> {
  const content = fs.readFileSync(p, "utf-8");
  return new Set(
    content
      .split(/\r?\n/)
      .map((l) => l.trim())
      .filter((l) => l.length > 0 && !l.startsWith("#"))
  );
}

function assertExternalInstallsAreGuardedToAll(output: string): void {
  const guard = 'if [[ "$skill_set" == "all" ]]';
  for (const source of EXTERNAL_SOURCES) {
    const sourcePosition = output.indexOf(source);
    expect(sourcePosition).toBeGreaterThan(-1);
    const guardStart = output.lastIndexOf(guard, sourcePosition);
    expect(guardStart).toBeGreaterThan(-1);
    const guardEnd = output.indexOf("\nfi", guardStart);
    expect(sourcePosition).toBeGreaterThan(guardStart);
    expect(sourcePosition).toBeLessThan(guardEnd);
  }
}

function npxCommands(output: string, operation: string): string[] {
  return output
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter((line) => line.includes(`${NPX_SKILLS} ${operation}`));
}

describe("install target modes", () => {
  test("install targets a consumer project with the workflow profile", () => {
    const output = renderJust("install", TARGET_PROJECT);

    expect(output).not.toContain("pip install");
    expect(output).toContain(SYNC_REFERENCES);
    expect(output).not.toContain("sync_shared_skill_runtime.py");
    expect(output).not.toContain(PACKAGED_REPO_SOURCE);
    expect(npxCommands(output, "add").length).toBe(1);
    for (const source of EXTERNAL_SOURCES) {
      expect(output).toContain(source);
    }
    assertExternalInstallsAreGuardedToAll(output);
    expect(output).toContain('if [[ "$skill_set" == "all" ]]');
    expect(output).toContain("prune-retired-local");
    expect(output).toContain("link-profile");
    expect(output).toContain(`--source-dir "${SOURCE_SKILLS_DIR}"`);
    expect(output).toContain(`target_dir='${TARGET_PROJECT}'`);
    expect(output).toContain('target_skills_dir="$target_dir/.agents/skills"');
    expect(output).toContain('--target-dir "$target_skills_dir"');
    expect(output).toContain('cd "$target_dir"');
    expect(output).not.toContain("record-installed");
    expect(output).not.toContain("--global");
    expect(output).toContain("set -euo pipefail");
    expect(output).toContain("skill_set='workflow'");
    expect(output).toContain("skill-sets/${skill_set}.txt");
  });

  for (const profile of PROFILE_NAMES) {
    test(`install accepts profile: ${profile}`, () => {
      const output = renderJust("install", TARGET_PROJECT, profile);
      expect(output).toContain(`target_dir='${TARGET_PROJECT}'`);
      expect(output).toContain(`skill_set='${profile}'`);
      expect(output).toContain("link-profile");
      expect(output).not.toContain(PACKAGED_REPO_SOURCE);
    });
  }

  test("install global preserves the packaged global workflow", () => {
    const output = renderJust("install-global");

    expect(output).toContain(SYNC_REFERENCES);
    expect(output).toContain(PACKAGED_REPO_SOURCE);
    expect(output).toContain("prune-retired");
    expect(output).toContain("link-profile");
    expect(output).toContain("record-installed");
    const adds = npxCommands(output, "add");
    expect(adds.length).toBeGreaterThan(0);
    expect(adds.every((cmd) => cmd.includes("--global"))).toBe(true);
  });

  test("install all adds only the pinned external profiles locally", () => {
    const output = renderJust("install", TARGET_PROJECT, "all");

    expect(readExternalProfile(ADDY_EXTERNAL_PROFILE)).toEqual(ADDY_SKILLS);
    const allSet = readProfile("all");
    for (const skill of EXTERNAL_SKILLS) {
      expect(allSet.has(skill)).toBe(false);
    }
    for (const source of EXTERNAL_SOURCES) {
      expect(output).toContain(source);
    }
    expect(output).toContain(ADDY_EXTERNAL_PROFILE);
    assertExternalInstallsAreGuardedToAll(output);
    expect(output.split(`${NPX_SKILLS} add`).length - 1).toBe(1);
    expect(output.split('install_external_profile "').length - 1).toBe(1);
    expect(output).toContain("external_skills");
    expect(output).not.toContain("combined_profile");
    expect(npxCommands(output, "add")[0]).not.toContain("--global");
  });

  test("uninstall targets a consumer project with the workflow profile", () => {
    const output = renderJust("uninstall", TARGET_PROJECT);

    expect(output).not.toContain("pip install");
    expect(output).not.toContain(SYNC_REFERENCES);
    expect(output).toContain("unlink-profile");
    expect(output).toContain("prune-retired-local");
    expect(output).toContain(`target_dir='${TARGET_PROJECT}'`);
    expect(output).toContain('target_skills_dir="$target_dir/.agents/skills"');
    expect(output).toContain('--target-dir "$target_skills_dir"');
  });

  test("uninstall global preserves the packaged global workflow", () => {
    const output = renderJust("uninstall-global");

    expect(output).toContain("prune-retired");
    expect(output).toContain("unlink-profile");
    expect(output).toContain("forget-profile");
  });
});
