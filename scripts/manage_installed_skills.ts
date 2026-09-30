#!/usr/bin/env bun
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import * as crypto from "node:crypto";
import * as process from "node:process";

export const SKILL_NAME_PATTERN = /^[a-z0-9][a-z0-9-]*$/;
export const REVISION_PATTERN = /^[0-9a-f]{40}$/;

export interface Retirement {
  name: string;
  revision: string;
}

export function defaultStatePath(): string {
  const override = process.env.SIRIUS_SKILLS_STATE_FILE;
  if (override) {
    return expandTilde(override);
  }
  const stateHome = process.env.XDG_STATE_HOME;
  const base = stateHome ? expandTilde(stateHome) : path.join(os.homedir(), ".local/state");
  return path.join(base, "sirius-skills/managed-skills.txt");
}

export function defaultCanonicalSkillsDir(): string {
  return path.join(os.homedir(), ".agents/skills");
}

export function defaultAntigravitySkillsDir(): string {
  return path.join(os.homedir(), ".gemini/config/skills");
}

function expandTilde(filepath: string): string {
  if (filepath === "~") return os.homedir();
  if (filepath.startsWith("~/") || filepath.startsWith("~\\")) {
    return path.join(os.homedir(), filepath.slice(2));
  }
  return filepath;
}

export function readNameFile(filePath: string): Set<string> {
  if (!fs.existsSync(filePath)) {
    return new Set<string>();
  }

  const names = new Set<string>();
  const content = fs.readFileSync(filePath, "utf-8");
  const lines = content.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const lineNumber = i + 1;
    const line = lines[i].trim();
    if (!line || line.startsWith("#")) {
      continue;
    }
    if (!SKILL_NAME_PATTERN.test(line)) {
      throw new Error(`${path.basename(filePath)}:${lineNumber}: invalid skill name '${line}'`);
    }
    names.add(line);
  }
  return names;
}

export function readRetirements(filePath: string): Retirement[] {
  const retirements: Retirement[] = [];
  const seen = new Set<string>();
  const content = fs.readFileSync(filePath, "utf-8");
  const lines = content.split(/\r?\n/);

  for (let i = 0; i < lines.length; i++) {
    const lineNumber = i + 1;
    const line = lines[i].trim();
    if (!line || line.startsWith("#")) {
      continue;
    }

    const fields = line.split("\t");
    if (
      fields.length !== 2 ||
      !SKILL_NAME_PATTERN.test(fields[0]) ||
      !REVISION_PATTERN.test(fields[1])
    ) {
      throw new Error(
        `${path.basename(filePath)}:${lineNumber}: expected skill<TAB>40-character evidence revision`
      );
    }

    const [name, revision] = fields;
    if (seen.has(name)) {
      throw new Error(`${path.basename(filePath)}:${lineNumber}: duplicate retired skill ${name}`);
    }
    seen.add(name);
    retirements.push({ name, revision });
  }

  return retirements;
}

export function parseInstalledSkills(payload: string): Set<string> {
  const data = JSON.parse(payload);
  if (!Array.isArray(data)) {
    throw new Error("installed skill data must be a JSON list");
  }

  const names = new Set<string>();
  for (const item of data) {
    if (typeof item !== "object" || item === null) {
      throw new Error("each installed skill entry must be an object");
    }
    const name = item.name;
    if (typeof name !== "string" || !name) {
      throw new Error("each installed skill entry must have a non-empty name");
    }
    names.add(name);
  }
  return names;
}

export function selectRetiredSkills(
  installedJson: string,
  options: {
    ledgerPath: string;
    statePath: string;
    includeUnowned?: boolean;
  }
): { selected: string[]; unowned: string[] } {
  const installed = parseInstalledSkills(installedJson);
  const retired = new Set(readRetirements(options.ledgerPath).map((entry) => entry.name));
  const owned = readNameFile(options.statePath);

  const candidates = new Set<string>();
  for (const name of installed) {
    if (retired.has(name)) {
      candidates.add(name);
    }
  }

  const selected = new Set<string>();
  if (options.includeUnowned) {
    for (const name of candidates) {
      selected.add(name);
    }
  } else {
    for (const name of candidates) {
      if (owned.has(name)) {
        selected.add(name);
      }
    }
  }

  const unowned = new Set<string>();
  for (const name of candidates) {
    if (!selected.has(name)) {
      unowned.add(name);
    }
  }

  return {
    selected: Array.from(selected).sort(),
    unowned: Array.from(unowned).sort(),
  };
}

export function writeNames(filePath: string, names: Iterable<string>): void {
  const normalized = Array.from(new Set(names)).sort();
  const invalid = normalized.filter((name) => !SKILL_NAME_PATTERN.test(name));
  if (invalid.length > 0) {
    throw new Error(`invalid skill name '${invalid[0]}'`);
  }

  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  const content = normalized.map((name) => `${name}\n`).join("");

  const tempPath = path.join(
    path.dirname(filePath),
    `.${path.basename(filePath)}.${crypto.randomUUID()}.tmp`
  );
  try {
    fs.writeFileSync(tempPath, content, "utf-8");
    fs.renameSync(tempPath, filePath);
  } finally {
    if (fs.existsSync(tempPath)) {
      try {
        fs.unlinkSync(tempPath);
      } catch {}
    }
  }
}

export function recordNames(names: Iterable<string>, statePath: string): void {
  const current = readNameFile(statePath);
  for (const name of names) {
    current.add(name);
  }
  writeNames(statePath, current);
}

export function forgetNames(names: Iterable<string>, statePath: string): void {
  const current = readNameFile(statePath);
  for (const name of names) {
    current.delete(name);
  }
  writeNames(statePath, current);
}

export function recordInstalled(profilePath: string, statePath: string): void {
  recordNames(readNameFile(profilePath), statePath);
}

export function forgetProfile(profilePath: string, statePath: string): void {
  forgetNames(readNameFile(profilePath), statePath);
}

export function forgetRetired(ledgerPath: string, statePath: string): void {
  forgetNames(
    readRetirements(ledgerPath).map((entry) => entry.name),
    statePath
  );
}

export function removeLockedProfile(
  profilePath: string,
  options: {
    lockPath: string;
    skillsDir: string;
    source: string;
  }
): void {
  const { lockPath, skillsDir, source } = options;
  if (!fs.existsSync(lockPath)) {
    return;
  }

  let lockLstat: fs.Stats;
  try {
    lockLstat = fs.lstatSync(lockPath);
  } catch {
    return;
  }
  if (lockLstat.isSymbolicLink()) {
    throw new Error(`project skill lock must not be a symlink: ${lockPath}`);
  }

  const lockContent = fs.readFileSync(lockPath, "utf-8");
  const lockData = JSON.parse(lockContent);
  if (
    typeof lockData !== "object" ||
    lockData === null ||
    typeof lockData.skills !== "object" ||
    lockData.skills === null
  ) {
    throw new Error("project skill lock must contain a skills object");
  }

  const entries = lockData.skills as Record<string, any>;
  const profileNames = Array.from(readNameFile(profilePath)).sort();
  const selected: Array<[string, string]> = [];

  for (const name of profileNames) {
    const entry = entries[name];
    if (entry === undefined) {
      continue;
    }
    if (typeof entry !== "object" || entry === null) {
      throw new Error(`project skill lock entry must be an object: ${name}`);
    }
    if (entry.source !== source) {
      continue;
    }

    const target = path.join(skillsDir, name);
    let targetExists = false;
    let targetIsSymlink = false;
    let targetIsDir = false;

    try {
      const stat = fs.lstatSync(target);
      targetExists = true;
      targetIsSymlink = stat.isSymbolicLink();
      targetIsDir = stat.isDirectory();
    } catch {}

    if (targetIsSymlink || targetIsDir || !targetExists) {
      selected.push([name, target]);
      continue;
    }
    throw new Error(`locked target skill is not a directory or symlink: ${target}`);
  }

  if (selected.length === 0) {
    return;
  }

  for (const [name] of selected) {
    delete entries[name];
  }

  const tempPath = path.join(
    path.dirname(lockPath),
    `.${path.basename(lockPath)}.${crypto.randomUUID()}.tmp`
  );
  try {
    fs.writeFileSync(tempPath, JSON.stringify(lockData, null, 2) + "\n", "utf-8");
    for (const [_name, target] of selected) {
      try {
        const stat = fs.lstatSync(target);
        if (stat.isSymbolicLink()) {
          fs.unlinkSync(target);
        } else if (stat.isDirectory()) {
          fs.rmSync(target, { recursive: true, force: true });
        }
      } catch {}
    }
    fs.renameSync(tempPath, lockPath);
  } finally {
    if (fs.existsSync(tempPath)) {
      try {
        fs.unlinkSync(tempPath);
      } catch {}
    }
  }
}

function canonicalizePath(p: string): string {
  try {
    return fs.realpathSync(p);
  } catch {
    const resolved = path.resolve(p);
    try {
      const dir = fs.realpathSync(path.dirname(resolved));
      return path.join(dir, path.basename(resolved));
    } catch {
      return resolved;
    }
  }
}

export function linkPointsTo(linkPath: string, expectedTarget: string): boolean {
  try {
    const stat = fs.lstatSync(linkPath);
    if (!stat.isSymbolicLink()) {
      return false;
    }
    let rawTarget = fs.readlinkSync(linkPath);
    if (!path.isAbsolute(rawTarget)) {
      rawTarget = path.resolve(path.dirname(linkPath), rawTarget);
    }
    return canonicalizePath(rawTarget) === canonicalizePath(expectedTarget);
  } catch {
    return false;
  }
}

export function skillRootsAreEquivalent(sourceDir: string, targetDir: string): boolean {
  return canonicalizePath(sourceDir) === canonicalizePath(targetDir);
}

export function linkNames(
  names: Iterable<string>,
  options: {
    sourceDir: string;
    targetDir: string;
  }
): void {
  const { sourceDir, targetDir } = options;
  const normalized = Array.from(new Set(names)).sort();
  if (skillRootsAreEquivalent(sourceDir, targetDir)) {
    return;
  }

  try {
    const lstat = fs.lstatSync(targetDir);
    if (lstat.isSymbolicLink()) {
      try {
        const stat = fs.statSync(targetDir);
        if (!stat.isDirectory()) {
          throw new Error(`target skill directory is a broken link: ${targetDir}`);
        }
      } catch {
        throw new Error(`target skill directory is a broken link: ${targetDir}`);
      }
    } else if (!lstat.isDirectory()) {
      throw new Error(`target skill directory is not a directory: ${targetDir}`);
    }
  } catch (err: any) {
    if (err.code !== "ENOENT") {
      throw err;
    }
  }

  const linksToCreate: Array<[string, string]> = [];
  for (const name of normalized) {
    const source = path.join(sourceDir, name);
    const target = path.join(targetDir, name);

    let sourceIsDir = false;
    try {
      sourceIsDir = fs.statSync(source).isDirectory();
    } catch {}

    if (!sourceIsDir) {
      throw new Error(`source skill directory is missing: ${source}`);
    }

    let targetLstat: fs.Stats | null = null;
    try {
      targetLstat = fs.lstatSync(target);
    } catch {}

    if (targetLstat) {
      if (targetLstat.isSymbolicLink()) {
        if (linkPointsTo(target, source)) {
          continue;
        }
        throw new Error(`refusing to replace existing target skill: ${target}`);
      }
      throw new Error(`refusing to replace existing target skill: ${target}`);
    }

    linksToCreate.push([source, target]);
  }

  fs.mkdirSync(targetDir, { recursive: true });
  for (const [source, target] of linksToCreate) {
    const relativeSource = path.relative(path.dirname(target), source);
    fs.symlinkSync(relativeSource, target, "dir");
  }
}

export function unlinkNames(
  names: Iterable<string>,
  options: {
    sourceDir: string;
    targetDir: string;
  }
): void {
  const { sourceDir, targetDir } = options;
  if (skillRootsAreEquivalent(sourceDir, targetDir)) {
    return;
  }

  for (const name of Array.from(new Set(names)).sort()) {
    const source = path.join(sourceDir, name);
    const target = path.join(targetDir, name);
    if (linkPointsTo(target, source)) {
      try {
        fs.unlinkSync(target);
      } catch {}
    }
  }
}

export function linkProfile(
  profilePath: string,
  options: {
    sourceDir: string;
    targetDir: string;
  }
): void {
  linkNames(readNameFile(profilePath), options);
}

export function unlinkProfile(
  profilePath: string,
  options: {
    sourceDir: string;
    targetDir: string;
  }
): void {
  unlinkNames(readNameFile(profilePath), options);
}

export function unlinkRetired(
  ledgerPath: string,
  options: {
    statePath: string;
    sourceDir: string;
    targetDir: string;
    includeUnowned?: boolean;
  }
): void {
  const retired = new Set(readRetirements(ledgerPath).map((entry) => entry.name));
  const names = options.includeUnowned
    ? Array.from(retired)
    : Array.from(retired).filter((name) => readNameFile(options.statePath).has(name));
  unlinkNames(names, {
    sourceDir: options.sourceDir,
    targetDir: options.targetDir,
  });
}

function parseCliArgs(argv: string[]) {
  let state = defaultStatePath();
  let command = "";
  let ledger = "";
  let profile = "";
  let lock = "";
  let skillsDir = "";
  let source = "";
  let sourceDir = defaultCanonicalSkillsDir();
  let targetDir = defaultAntigravitySkillsDir();
  let includeUnowned = false;

  let i = 0;
  while (i < argv.length) {
    const arg = argv[i];
    if (arg === "--state") {
      state = argv[++i];
    } else if (arg.startsWith("--state=")) {
      state = arg.slice("--state=".length);
    } else if (!arg.startsWith("-") && !command) {
      command = arg;
    } else if (arg === "--ledger") {
      ledger = argv[++i];
    } else if (arg.startsWith("--ledger=")) {
      ledger = arg.slice("--ledger=".length);
    } else if (arg === "--profile") {
      profile = argv[++i];
    } else if (arg.startsWith("--profile=")) {
      profile = arg.slice("--profile=".length);
    } else if (arg === "--lock") {
      lock = argv[++i];
    } else if (arg.startsWith("--lock=")) {
      lock = arg.slice("--lock=".length);
    } else if (arg === "--skills-dir") {
      skillsDir = argv[++i];
    } else if (arg.startsWith("--skills-dir=")) {
      skillsDir = arg.slice("--skills-dir=".length);
    } else if (arg === "--source") {
      source = argv[++i];
    } else if (arg.startsWith("--source=")) {
      source = arg.slice("--source=".length);
    } else if (arg === "--source-dir") {
      sourceDir = argv[++i];
    } else if (arg.startsWith("--source-dir=")) {
      sourceDir = arg.slice("--source-dir=".length);
    } else if (arg === "--target-dir") {
      targetDir = argv[++i];
    } else if (arg.startsWith("--target-dir=")) {
      targetDir = arg.slice("--target-dir=".length);
    } else if (arg === "--include-unowned") {
      includeUnowned = true;
    } else {
      throw new Error(`unrecognized argument: ${arg}`);
    }
    i++;
  }

  if (!command) {
    throw new Error("subcommand required");
  }

  return {
    command,
    state,
    ledger,
    profile,
    lock,
    skillsDir,
    source,
    sourceDir,
    targetDir,
    includeUnowned,
  };
}

async function readAllStdin(): Promise<string> {
  let data = "";
  for await (const chunk of process.stdin) {
    data += chunk;
  }
  return data;
}

export async function main(argv: string[] = process.argv.slice(2)): Promise<number> {
  try {
    const args = parseCliArgs(argv);
    if (args.command === "select-retired") {
      if (!args.ledger) {
        throw new Error("--ledger required");
      }
      const stdinData = await readAllStdin();
      const { selected, unowned } = selectRetiredSkills(stdinData, {
        ledgerPath: args.ledger,
        statePath: args.state,
        includeUnowned: args.includeUnowned,
      });
      if (selected.length > 0) {
        console.log(selected.join("\n"));
      }
      if (unowned.length > 0) {
        console.error(
          "Retired skill names are installed but ownership is unknown: " + unowned.join(", ")
        );
        console.error(
          "Review them, then run `just prune-retired-legacy` to remove those names explicitly."
        );
      }
    } else if (args.command === "record-installed") {
      if (!args.profile) throw new Error("--profile required");
      recordInstalled(args.profile, args.state);
    } else if (args.command === "remove-locked-profile") {
      if (!args.profile) throw new Error("--profile required");
      if (!args.lock) throw new Error("--lock required");
      if (!args.skillsDir) throw new Error("--skills-dir required");
      if (!args.source) throw new Error("--source required");
      removeLockedProfile(args.profile, {
        lockPath: args.lock,
        skillsDir: args.skillsDir,
        source: args.source,
      });
    } else if (args.command === "link-profile") {
      if (!args.profile) throw new Error("--profile required");
      linkProfile(args.profile, {
        sourceDir: args.sourceDir,
        targetDir: args.targetDir,
      });
    } else if (args.command === "unlink-profile") {
      if (!args.profile) throw new Error("--profile required");
      unlinkProfile(args.profile, {
        sourceDir: args.sourceDir,
        targetDir: args.targetDir,
      });
    } else if (args.command === "unlink-retired") {
      if (!args.ledger) throw new Error("--ledger required");
      unlinkRetired(args.ledger, {
        statePath: args.state,
        sourceDir: args.sourceDir,
        targetDir: args.targetDir,
        includeUnowned: args.includeUnowned,
      });
    } else if (args.command === "forget-profile") {
      if (!args.profile) throw new Error("--profile required");
      forgetProfile(args.profile, args.state);
    } else if (args.command === "forget-retired") {
      if (!args.ledger) throw new Error("--ledger required");
      forgetRetired(args.ledger, args.state);
    } else {
      throw new Error(`unknown command: ${args.command}`);
    }
  } catch (exc: any) {
    console.error(`Failed to manage installed skills: ${exc.message}`);
    return 1;
  }
  return 0;
}

if (import.meta.main) {
  main().then((code) => {
    if (code !== 0) {
      process.exit(code);
    }
  });
}
