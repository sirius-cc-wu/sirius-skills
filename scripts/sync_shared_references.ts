#!/usr/bin/env bun
import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const repoRoot = resolve(__dirname, "..");

const REFERENCE_RELATIVE_PATH = "docs/shared/config-surface-governance.md";
const TARGET_RELATIVE_PATHS = [
  "skills/behavior-preserving-refactoring/references/config-surface-governance.md",
];

function syncOne(source: string, target: string): "unchanged" | "updated" {
  mkdirSync(dirname(target), { recursive: true });
  if (
    existsSync(target) &&
    readFileSync(target, "utf-8") === readFileSync(source, "utf-8")
  ) {
    return "unchanged";
  }

  copyFileSync(source, target);
  return "updated";
}

export function main(argv: string[] = process.argv.slice(2)): number {
  if (argv.length > 0) {
    console.error("sync-shared-references does not accept arguments.");
    return 2;
  }

  const source = join(repoRoot, REFERENCE_RELATIVE_PATH);
  const targets = TARGET_RELATIVE_PATHS.map((p) => join(repoRoot, p));

  if (!existsSync(source)) {
    console.error(`Missing shared reference: ${source}`);
    return 1;
  }

  try {
    for (const target of targets) {
      const status = syncOne(source, target);
      console.log(`${status}: ${relative(repoRoot, target)}`);
    }
  } catch (exc) {
    console.error(`Failed to sync shared references: ${exc}`);
    return 1;
  }

  return 0;
}

if (import.meta.main) {
  process.exit(main());
}
