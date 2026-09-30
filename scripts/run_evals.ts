#!/usr/bin/env bun
import * as path from "node:path";
import * as process from "node:process";
import { evaluateRepository } from "./evals/routing";

export function findRepoRoot(): string {
  return path.resolve(__dirname, "..");
}

function parseCliArgs(argv: string[]) {
  let root = findRepoRoot();
  let behavioral: string | null = null;
  let caseId: string | null = null;
  let dryRun = false;

  let i = 0;
  while (i < argv.length) {
    const arg = argv[i];
    if (arg === "--root") {
      root = path.resolve(argv[++i]);
    } else if (arg.startsWith("--root=")) {
      root = path.resolve(arg.slice("--root=".length));
    } else if (arg === "--behavioral") {
      behavioral = argv[++i];
    } else if (arg.startsWith("--behavioral=")) {
      behavioral = arg.slice("--behavioral=".length);
    } else if (arg === "--case") {
      caseId = argv[++i];
    } else if (arg.startsWith("--case=")) {
      caseId = arg.slice("--case=".length);
    } else if (arg === "--dry-run") {
      dryRun = true;
    }
    i++;
  }

  return { root, behavioral, caseId, dryRun };
}

export async function main(argv: string[] = process.argv.slice(2)): Promise<number> {
  const args = parseCliArgs(argv);

  if (args.behavioral) {
    console.error("Behavioral evaluations will be available in Slice 03.");
    return 1;
  }

  const report = evaluateRepository(args.root);

  console.log(
    `Evaluated ${report.skillCount} skills across ${report.caseFiles} routing case files.`
  );
  for (const warning of report.warnings) {
    console.log(`WARN: ${warning}`);
  }
  for (const error of report.errors) {
    console.log(`ERROR: ${error}`);
  }

  const rate =
    report.rankOneRate === null
      ? "n/a"
      : `${Math.round(report.rankOneRate * 100)}%`;

  console.log(
    `Routing checks: ${report.routingPassed}/${report.routingChecks} passed; positive rank-one rate: ${rate}.`
  );

  return report.errors.length > 0 ? 1 : 0;
}

if (import.meta.main) {
  main().then((code) => {
    if (code !== 0) {
      process.exit(code);
    }
  });
}
