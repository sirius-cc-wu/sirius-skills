#!/usr/bin/env bun
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { resolve, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const root = resolve(__dirname, "..");

const skillCatalog = join(root, "catalog/skills.md");
const sourceCatalog = join(root, "catalog/sources.md");
const relationshipGuide = join(root, "catalog/skill-relationships.md");
const relationshipSvg = join(root, "catalog/skill-relationships.svg");
const trackDirectory = join(root, "catalog/tracks");
const profileDirectory = join(root, "skill-sets");
const allProfile = join(profileDirectory, "all.txt");
const retiredLedger = join(root, "catalog/retired-skills.tsv");
const externalProfiles = [
  join(root, "catalog/external-skill-sets/addy-osmani.txt"),
];

function fail(message: string): never {
  console.error(message);
  process.exit(1);
}

function readProfile(filePath: string): string[] {
  if (!existsSync(filePath)) {
    fail(`missing profile file: ${filePath}`);
  }
  return readFileSync(filePath, "utf-8")
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0 && !line.startsWith("#"));
}

// 1. Core file existence checks
if (!existsSync(join(root, "README.md"))) fail("missing README.md");
if (!existsSync(join(root, "AGENTS.md"))) fail("missing AGENTS.md");
if (!existsSync(skillCatalog)) fail(`missing ${skillCatalog}`);
if (!existsSync(sourceCatalog)) fail(`missing ${sourceCatalog}`);
if (!existsSync(relationshipGuide)) fail(`missing ${relationshipGuide}`);
if (!existsSync(relationshipSvg)) fail(`missing ${relationshipSvg}`);
if (!existsSync(trackDirectory) || !statSync(trackDirectory).isDirectory()) {
  fail(`missing ${trackDirectory}`);
}
if (!existsSync(allProfile)) fail(`missing ${allProfile}`);
if (!existsSync(retiredLedger)) fail(`missing ${retiredLedger}`);

// 2. Profile validation
const profiles = [
  "workflow",
  "iterative-design",
  "applying-uml-and-patterns",
  "reverse-engineering",
  "all",
];

for (const profile of profiles) {
  const file = join(profileDirectory, `${profile}.txt`);
  if (!existsSync(file)) fail(`missing skill profile ${profile}`);
  const members = readProfile(file);
  if (members.length === 0) fail(`skill profile is empty: ${profile}`);

  const seen = new Set<string>();
  const duplicates = new Set<string>();
  for (const m of members) {
    if (seen.has(m)) duplicates.add(m);
    seen.add(m);
  }
  if (duplicates.size > 0) {
    fail(`duplicate skills in ${profile}: ${Array.from(duplicates).join(" ")}`);
  }
}

// Alias equality check
const iterativeDesignMembers = readProfile(join(profileDirectory, "iterative-design.txt")).sort();
const applyingUmlMembers = readProfile(join(profileDirectory, "applying-uml-and-patterns.txt")).sort();
if (iterativeDesignMembers.length !== applyingUmlMembers.length ||
    !iterativeDesignMembers.every((val, idx) => val === applyingUmlMembers[idx])) {
  fail("applying-uml-and-patterns must remain an alias for iterative-design");
}

// all.txt must list every deployable skill in skills/ exactly once
const expected = readProfile(allProfile);
const skillsDir = join(root, "skills");
const discovered: string[] = [];
for (const entry of readdirSync(skillsDir, { withFileTypes: true })) {
  if (entry.isDirectory() && existsSync(join(skillsDir, entry.name, "SKILL.md"))) {
    discovered.push(entry.name);
  }
}
discovered.sort();
const expectedSorted = [...expected].sort();
if (expectedSorted.length !== discovered.length ||
    !expectedSorted.every((val, idx) => val === discovered[idx])) {
  fail("skill-sets/all.txt must list every deployable skill exactly once");
}

const managedByName = new Set<string>(expected);

// 3. Retired skills ledger validation
const retiredByName = new Map<string, string>();
let retiredCount = 0;
const retiredContent = readFileSync(retiredLedger, "utf-8");
for (const rawLine of retiredContent.split("\n")) {
  const line = rawLine.trim();
  if (!line || line.startsWith("#")) continue;

  const parts = line.split("\t");
  if (parts.length !== 2) fail(`malformed retired skill entry: ${line}`);
  const [name, revision] = parts;
  if (!/^[a-z0-9][a-z0-9-]*$/.test(name)) fail(`invalid retired skill name: ${name}`);
  if (!/^[0-9a-f]{40}$/.test(revision)) fail(`invalid retirement evidence revision for ${name}`);
  if (retiredByName.has(name)) fail(`duplicate retired skill: ${name}`);
  if (managedByName.has(name)) fail(`active skill is also retired: ${name}`);
  if (existsSync(join(root, "skills", name))) fail(`retired skill still has a package: ${name}`);

  retiredByName.set(name, revision);
  retiredCount++;
}

if (retiredCount === 0) fail("retired skill ledger is empty");

// 4. External profiles validation
const externalByName = new Set<string>();
let externalCount = 0;
for (const extProfile of externalProfiles) {
  if (!existsSync(extProfile)) fail(`missing external skill profile: ${extProfile}`);
  const rawContent = readFileSync(extProfile, "utf-8");
  if (!/^# Source revision: [0-9a-f]{40}$/m.test(rawContent)) {
    fail(`external skill profile missing pinned source revision: ${extProfile}`);
  }
  const extSkills = readProfile(extProfile);
  if (extSkills.length === 0) fail(`external skill profile is empty: ${extProfile}`);

  for (const name of extSkills) {
    if (!/^[a-z0-9][a-z0-9-]*$/.test(name)) fail(`invalid external skill name: ${name}`);
    if (externalByName.has(name)) fail(`duplicate external skill: ${name}`);
    if (managedByName.has(name)) fail(`external skill is active in Sirius catalog: ${name}`);
    if (retiredByName.has(name)) fail(`external skill is retired in Sirius ledger: ${name}`);
    externalByName.add(name);
    externalCount++;
  }
}

// 5. Profile member existence check
for (const profile of profiles) {
  const file = join(profileDirectory, `${profile}.txt`);
  for (const name of readProfile(file)) {
    if (!managedByName.has(name)) {
      fail(`${profile} references unmanaged skill ${name}`);
    }
  }
}

// 6. Workflow tracks existence
const requiredTracks = [
  "repository-workflow",
  "client-to-code",
  "reverse-engineering",
  "iterative-analysis-design",
  "implementation-evolution",
];
for (const name of requiredTracks) {
  const trackFile = join(trackDirectory, `${name}.md`);
  if (!existsSync(trackFile)) fail(`missing workflow track ${name}`);
}

// 7. Universal skill structure checks
const catalogContent = readFileSync(skillCatalog, "utf-8");
for (const name of expected) {
  if (!/^[a-z0-9-]+$/.test(name)) fail(`invalid skill name in managed set: ${name}`);
  const skillFile = join(root, "skills", name, "SKILL.md");
  if (!existsSync(skillFile)) fail(`missing ${skillFile}`);
  const content = readFileSync(skillFile, "utf-8");

  if (!new RegExp(`^name:\\s*${name}$`, "m").test(content)) {
    fail(`bad or missing name in ${skillFile}`);
  }
  if (!/^description:\s*.+/m.test(content)) {
    fail(`bad or missing description in ${skillFile}`);
  }

  // Description format check
  const descMatch = content.match(/^description:\s*(.+)$/m);
  if (descMatch) {
    const desc = descMatch[1].trim();
    if (desc.includes(": ") && !desc.startsWith('"') && !desc.startsWith("'") && !desc.startsWith(">-") && !desc.startsWith("|")) {
      fail(`description containing ': ' must be YAML-quoted in ${skillFile}`);
    }
  }

  if (!/^## Workflow/m.test(content)) fail(`missing Workflow in ${skillFile}`);
  if (!catalogContent.includes(`| \`${name}\` |`)) {
    fail(`skill catalog missing ${name}`);
  }
}

// 8. Shared reference check
const sharedReference = join(root, "docs/shared/config-surface-governance.md");
if (!existsSync(sharedReference)) fail(`missing ${sharedReference}`);
const sharedTargets = [
  join(root, "skills/behavior-preserving-refactoring/references/config-surface-governance.md"),
];
for (const target of sharedTargets) {
  if (!existsSync(target)) fail(`missing ${target}`);
  if (readFileSync(sharedReference, "utf-8") !== readFileSync(target, "utf-8")) {
    fail(`shared reference is out of sync: ${target}`);
  }
}

// 9. Documentation specialist skills checks
const iterativeAndReverse = new Set([
  ...readProfile(join(profileDirectory, "iterative-design.txt")),
  ...readProfile(join(profileDirectory, "reverse-engineering.txt")),
]);
const workflowSet = new Set(readProfile(join(profileDirectory, "workflow.txt")));
const specialistSkills = Array.from(iterativeAndReverse).filter((x) => !workflowSet.has(x));

for (const name of specialistSkills) {
  const skillFile = join(root, "skills", name, "SKILL.md");
  const content = readFileSync(skillFile, "utf-8");
  if (!/^## When to Use/m.test(content)) fail(`missing When to Use in ${skillFile}`);
  if (!content.includes("artifact-selection-budget.md")) {
    fail(`missing artifact selection budget guidance in ${skillFile}`);
  }
  if (name !== "select-technical-artifacts") {
    if (!content.includes("markdown-artifact-frontmatter.md")) {
      fail(`missing Markdown artifact frontmatter guidance in ${skillFile}`);
    }
  }
  if (!/^## Verification/m.test(content)) fail(`missing Verification in ${skillFile}`);
}

// 10. Specific references & metadata checks
const selectionSkill = join(root, "skills/select-technical-artifacts/SKILL.md");
const selectionMetadata = join(root, "skills/select-technical-artifacts/agents/openai.yaml");
const layoutSkill = join(root, "skills/design-repository-artifact-layout/SKILL.md");
const layoutReference = join(root, "skills/design-repository-artifact-layout/references/artifact-layouts.md");
const budgetReference = join(root, "skills/select-technical-artifacts/references/artifact-selection-budget.md");
const frontmatterReference = join(root, "skills/design-repository-artifact-layout/references/markdown-artifact-frontmatter.md");
const rustLifecycleSkill = join(root, "skills/design-rust-lifecycles/SKILL.md");
const rustLifecycleTemplate = join(root, "skills/design-rust-lifecycles/assets/rust-lifecycle-design.md");
const refactoringSkill = join(root, "skills/behavior-preserving-refactoring/SKILL.md");

if (!existsSync(layoutReference)) fail(`missing ${layoutReference}`);
if (!existsSync(budgetReference)) fail(`missing ${budgetReference}`);
if (!existsSync(frontmatterReference)) fail(`missing ${frontmatterReference}`);

if (!readFileSync(rustLifecycleSkill, "utf-8").includes("representative scenario")) {
  fail("Rust lifecycle skill missing system-context input");
}
if (!/^## Design Context and Responsibility Inputs$/m.test(readFileSync(rustLifecycleTemplate, "utf-8"))) {
  fail("Rust lifecycle template missing responsibility inputs");
}
if (!/^## Completion Boundary$/m.test(readFileSync(rustLifecycleTemplate, "utf-8"))) {
  fail("Rust lifecycle template missing completion boundary");
}
if (!readFileSync(refactoringSkill, "utf-8").includes("Classify boundary impact")) {
  fail("refactoring skill missing boundary-impact classification");
}
if (!/^## Creation Gate$/m.test(readFileSync(budgetReference, "utf-8"))) {
  fail("artifact budget missing creation gate");
}
if (!/^## Disposition Order$/m.test(readFileSync(budgetReference, "utf-8"))) {
  fail("artifact budget missing disposition guidance");
}

if (!existsSync(selectionMetadata)) fail("select-technical-artifacts missing agents/openai.yaml");
if (!readFileSync(selectionMetadata, "utf-8").includes("$select-technical-artifacts")) {
  fail("artifact selection metadata missing skill invocation");
}
if (!/^## Output$/m.test(readFileSync(selectionSkill, "utf-8"))) {
  fail("artifact selection skill missing output guidance");
}
if (!/^## Boundaries$/m.test(readFileSync(selectionSkill, "utf-8"))) {
  fail("artifact selection skill missing boundary guidance");
}
if (!readFileSync(selectionSkill, "utf-8").includes("keep with implementation")) {
  fail("artifact selection skill missing executable disposition");
}
if (!readFileSync(selectionSkill, "utf-8").includes("authorizes updating an existing artifact budget or plan")) {
  fail("artifact selection skill missing authorized budget-update mode");
}
if (!/^## Output$/m.test(readFileSync(layoutSkill, "utf-8"))) {
  fail("artifact layout skill missing output guidance");
}
if (!/^## Artifact Lifecycles$/m.test(readFileSync(layoutReference, "utf-8"))) {
  fail("artifact layout reference missing lifecycle guidance");
}
if (!/^## Layout Options$/m.test(readFileSync(layoutReference, "utf-8"))) {
  fail("artifact layout reference missing layout options");
}
if (!/^## Idea Placement$/m.test(readFileSync(layoutReference, "utf-8"))) {
  fail("artifact layout reference missing idea placement guidance");
}
if (!/^## Linking Rules$/m.test(readFileSync(layoutReference, "utf-8"))) {
  fail("artifact layout reference missing linking rules");
}
if (!/^type:\s*"\[Descriptive artifact type\]"$/m.test(readFileSync(frontmatterReference, "utf-8"))) {
  fail("frontmatter reference missing base type field");
}

const layoutMetadata = join(root, "skills/design-repository-artifact-layout/agents/openai.yaml");
if (!existsSync(layoutMetadata)) fail("design-repository-artifact-layout missing agents/openai.yaml");
if (!readFileSync(layoutMetadata, "utf-8").includes("$design-repository-artifact-layout")) {
  fail("artifact layout metadata missing skill invocation");
}

// 11. Template types frontmatter check
const templateTypes = [
  ["assess-development-input", "Development Input Assessment"],
  ["vision", "Vision"],
  ["specify-quality-constraints", "Supplementary Specification"],
  ["design-rust-lifecycles", "Rust Lifecycle Design"],
  ["behavior-preserving-refactoring", "Refactoring Record"],
];

for (const [name, type] of templateTypes) {
  const files = [join(root, "skills", name, "SKILL.md")];
  const refDir = join(root, "skills", name, "references");
  if (existsSync(refDir) && statSync(refDir).isDirectory()) {
    for (const ref of readdirSync(refDir)) {
      if (ref.endsWith(".md")) {
        files.push(join(refDir, ref));
      }
    }
  }
  const typeRegex = new RegExp(`^type:\\s*"${type}"$`, "m");
  const found = files.some((f) => existsSync(f) && typeRegex.test(readFileSync(f, "utf-8")));
  if (!found) fail(`${name} template missing type: ${type}`);
}

// 12. Catalog & documentation content checks
if (!/^# Skill Catalog$/m.test(catalogContent)) fail("skill catalog missing title");
if (!/^# Source Catalog$/m.test(readFileSync(sourceCatalog, "utf-8"))) {
  fail("source catalog missing title");
}
const relGuideContent = readFileSync(relationshipGuide, "utf-8");
if (!/^@startuml sirius-skills-birds-eye$/m.test(relGuideContent)) {
  fail("relationship guide missing embedded overview PlantUML");
}
const plantumlCount = (relGuideContent.match(/^```plantuml$/gm) || []).length;
if (plantumlCount !== 4) {
  fail("relationship guide must retain four embedded PlantUML views");
}
if (!readFileSync(relationshipSvg, "utf-8").includes("<svg ")) {
  fail("relationship overview is not SVG");
}

const readmeContent = readFileSync(join(root, "README.md"), "utf-8");
if (!readmeContent.includes("catalog/skill-relationships.svg")) {
  fail("README missing relationship overview");
}
if (!/^## Catalog and workflow tracks$/m.test(readmeContent)) {
  fail("README missing workflow tracks");
}
if (!/^## Consolidation history$/m.test(readmeContent)) {
  fail("README missing consolidation history");
}

console.log(`Validated ${expected.length} skills across ${profiles.length} profiles.`);
console.log(`Validated ${externalCount} external add-on skills across ${externalProfiles.length} source profiles.`);
console.log(`Validated ${retiredCount} retired skill tombstones.`);
