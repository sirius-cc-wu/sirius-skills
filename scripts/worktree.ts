#!/usr/bin/env bun
/**
 * Worktree management utility for autonomous agent and builder fleet isolation.
 */

import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import { basename, dirname, join, resolve } from "node:path";
import { parseArgs } from "node:util";

export interface WorktreeResult {
  status: "created" | "exists" | "removed" | "pruned" | "error";
  branch: string;
  path: string;
  message?: string;
  error?: string;
  branch_deleted?: boolean;
}

export interface WorktreeInfo {
  path: string;
  head?: string;
  branch?: string;
}

export async function getRepoRoot(cwd?: string): Promise<string> {
  const prefix = cwd ? ["git", "-C", cwd] : ["git"];

  const toplevel = await Bun.$`${prefix} rev-parse --show-toplevel`.nothrow().quiet();
  if (toplevel.exitCode === 0 && toplevel.text().trim()) {
    return resolve(cwd ?? process.cwd(), toplevel.text().trim());
  }

  const commonDir = await Bun.$`${prefix} -c safe.bareRepository=all rev-parse --git-common-dir`.nothrow().quiet();
  if (commonDir.exitCode === 0 && commonDir.text().trim()) {
    return resolve(cwd ?? process.cwd(), commonDir.text().trim());
  }

  const gitDir = await Bun.$`${prefix} -c safe.bareRepository=all rev-parse --git-dir`.nothrow().quiet();
  if (gitDir.exitCode === 0 && gitDir.text().trim()) {
    return resolve(cwd ?? process.cwd(), gitDir.text().trim());
  }

  throw new Error(`Failed to determine repository root: ${toplevel.stderr.toString().trim()}`);
}

export function parseWorktreePorcelain(output: string): WorktreeInfo[] {
  const lines = output.split("\n");
  const worktrees: WorktreeInfo[] = [];
  let current: WorktreeInfo | null = null;

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (line.startsWith("worktree ")) {
      if (current) {
        worktrees.push(current);
      }
      current = { path: line.slice("worktree ".length).trim() };
    } else if (line.startsWith("HEAD ") && current) {
      current.head = line.slice("HEAD ".length).trim();
    } else if (line.startsWith("branch ") && current) {
      const ref = line.slice("branch ".length).trim();
      current.branch = ref.replace("refs/heads/", "");
    } else if (line === "detached" && current) {
      current.branch = "(detached)";
    }
  }

  if (current) {
    worktrees.push(current);
  }

  return worktrees;
}

export function detectWorktreePool(worktrees: WorktreeInfo[], repoRoot: string): string | null {
  const resolvedRoot = resolve(repoRoot);
  const dirCounts = new Map<string, number>();

  for (const wt of worktrees) {
    const wtPath = resolve(wt.path);
    if (wtPath === resolvedRoot) {
      continue;
    }
    const parentDir = dirname(wtPath);
    if (parentDir === resolvedRoot) {
      continue;
    }
    dirCounts.set(parentDir, (dirCounts.get(parentDir) ?? 0) + 1);
  }

  if (dirCounts.size === 0) {
    return null;
  }

  let bestDir: string | null = null;
  let maxCount = 0;
  for (const [dir, count] of dirCounts.entries()) {
    if (count > maxCount) {
      maxCount = count;
      bestDir = dir;
    }
  }

  return bestDir;
}

export function getWorktreesDir(repoRoot: string): string {
  const envDir = (
    process.env.WORKTREES_DIR ||
    process.env.SIRIUS_WORKTREES_DIR ||
    process.env.FOXPILOT_WORKTREES_DIR
  )?.trim();
  if (envDir) {
    const resolved = resolve(repoRoot, envDir);
    if (!existsSync(resolved)) {
      mkdirSync(resolved, { recursive: true });
    }
    return resolved;
  }

  for (const configKey of ["sirius.worktreesDir", "foxpilot.worktreesDir", "worktree.poolDir"]) {
    try {
      const res = spawnSync("git", ["-C", repoRoot, "config", "--get", configKey], {
        encoding: "utf-8",
      });
      const configDir = res.status === 0 ? res.stdout.trim() : "";
      if (configDir) {
        const resolved = resolve(repoRoot, configDir);
        if (!existsSync(resolved)) {
          mkdirSync(resolved, { recursive: true });
        }
        return resolved;
      }
    } catch {
      // Ignore error
    }
  }

  try {
    const res = spawnSync("git", ["-C", repoRoot, "worktree", "list", "--porcelain"], {
      encoding: "utf-8",
    });
    if (res.status === 0 && res.stdout.trim()) {
      const worktrees = parseWorktreePorcelain(res.stdout);
      const poolDir = detectWorktreePool(worktrees, repoRoot);
      if (poolDir) {
        if (!existsSync(poolDir)) {
          mkdirSync(poolDir, { recursive: true });
        }
        return poolDir;
      }
    }
  } catch {
    // Ignore error
  }

  const worktreesDir = join(repoRoot, ".worktrees");
  if (!existsSync(worktreesDir)) {
    mkdirSync(worktreesDir, { recursive: true });
  }
  return worktreesDir;
}

export async function resolveWorktreesDir(repoRoot: string): Promise<string> {
  return getWorktreesDir(repoRoot);
}

export async function branchExists(branch: string, repoRoot: string): Promise<boolean> {
  const result = await Bun.$`git -C ${repoRoot} show-ref --verify refs/heads/${branch}`.nothrow().quiet();
  return result.exitCode === 0;
}

export async function remoteBranchExists(branch: string, repoRoot: string): Promise<boolean> {
  const result = await Bun.$`git -C ${repoRoot} show-ref --verify refs/remotes/origin/${branch}`.nothrow().quiet();
  return result.exitCode === 0;
}

export async function createWorktree(
  name: string,
  baseBranch?: string | null,
  repoRoot?: string
): Promise<WorktreeResult> {
  const root = repoRoot ?? (await getRepoRoot());
  const worktreesDir = await resolveWorktreesDir(root);
  const safeName = name.replace(/\//g, "-");
  const targetPath = join(worktreesDir, safeName);

  if (existsSync(targetPath)) {
    return {
      status: "exists",
      branch: name,
      path: targetPath,
      message: `Worktree at ${targetPath} already exists`,
    };
  }

  let exitCode: number;
  let stderr = "";
  let stdout = "";

  if (await branchExists(name, root)) {
    const res = await Bun.$`git -C ${root} worktree add ${targetPath} ${name}`.nothrow().quiet();
    exitCode = res.exitCode;
    stderr = res.stderr.toString();
    stdout = res.stdout.toString();
  } else if (await remoteBranchExists(name, root)) {
    const res = await Bun.$`git -C ${root} worktree add -b ${name} ${targetPath} origin/${name}`.nothrow().quiet();
    exitCode = res.exitCode;
    stderr = res.stderr.toString();
    stdout = res.stdout.toString();
  } else {
    const args = ["git", "-C", root, "worktree", "add", "-b", name, targetPath];
    if (baseBranch) {
      args.push(baseBranch);
    }
    const res = await Bun.spawn(args, { stderr: "pipe", stdout: "pipe" });
    exitCode = await res.exited;
    stderr = await new Response(res.stderr).text();
    stdout = await new Response(res.stdout).text();
  }

  if (exitCode !== 0) {
    return {
      status: "error",
      branch: name,
      path: targetPath,
      error: stderr.trim() || stdout.trim(),
    };
  }

  return {
    status: "created",
    branch: name,
    path: targetPath,
    message: `Worktree created at ${targetPath} for branch ${name}`,
  };
}

export async function removeWorktree(
  name: string,
  options?: {
    force?: boolean;
    deleteBranch?: boolean;
    repoRoot?: string;
  }
): Promise<WorktreeResult> {
  const root = options?.repoRoot ?? (await getRepoRoot());
  const worktreesDir = await resolveWorktreesDir(root);
  const safeName = name.replace(/\//g, "-");

  const items = await listWorktrees(root);
  const resolvedRoot = resolve(root);
  const candidateItems = items.filter((item) => resolve(item.path) !== resolvedRoot);

  const matched = candidateItems.find((item) => {
    if (item.branch === name) return true;
    const base = basename(item.path);
    if (base === safeName || base === name) return true;
    if (item.path === name) return true;
    try {
      if (resolve(item.path) === resolve(name)) return true;
    } catch {
      // Ignore invalid path syntax
    }
    return false;
  });

  const targetPath = matched ? matched.path : join(worktreesDir, safeName);
  const branchToDelete =
    matched?.branch && matched.branch !== "(detached)" ? matched.branch : name;

  const removeArgs = ["git", "-C", root, "worktree", "remove", targetPath];
  if (options?.force) {
    removeArgs.push("--force");
  }

  const res = await Bun.spawn(removeArgs, { stderr: "pipe", stdout: "pipe" });
  const exitCode = await res.exited;
  const stderr = await new Response(res.stderr).text();
  const stdout = await new Response(res.stdout).text();

  let status: "removed" | "pruned" | "error";

  if (exitCode !== 0) {
    await Bun.$`git -C ${root} worktree prune`.nothrow().quiet();
    if (!existsSync(targetPath)) {
      status = "pruned";
    } else {
      return {
        status: "error",
        branch: branchToDelete,
        path: targetPath,
        error: stderr.trim() || stdout.trim(),
      };
    }
  } else {
    status = "removed";
  }

  await Bun.$`git -C ${root} worktree prune`.nothrow().quiet();

  let branchDeleted = false;
  if (options?.deleteBranch) {
    const delRes = await Bun.$`git -C ${root} branch -D ${branchToDelete}`.nothrow().quiet();
    branchDeleted = delRes.exitCode === 0;
  }

  return {
    status,
    branch: branchToDelete,
    path: targetPath,
    branch_deleted: branchDeleted,
    message: `Worktree ${targetPath} removed`,
  };
}

export async function listWorktrees(repoRoot?: string): Promise<WorktreeInfo[]> {
  const root = repoRoot ?? (await getRepoRoot());
  const res = await Bun.$`git -C ${root} worktree list --porcelain`.quiet();
  return parseWorktreePorcelain(res.text());
}

export function printUsage(out: (msg: string) => void = console.log): void {
  out(`Usage: worktree <command> [options]

Worktree management utility for autonomous agent and builder isolation.

Commands:
  create <branch> [base]       Create a new worktree for <branch> (optionally off [base])
  remove <branch|path> [opts]  Remove a worktree by branch name or path
  list [options]               List all active worktrees across the repository

Options:
  remove:
    -f, --force                Force removal even if uncommitted changes exist
    -d, --delete-branch        Also delete the Git branch associated with the worktree

  list:
    --json                     Output worktree list in JSON format

  global:
    -h, --help                 Show this help message

Environment & Configuration:
  WORKTREES_DIR, SIRIUS_WORKTREES_DIR, FOXPILOT_WORKTREES_DIR
                               Override default worktree pool directory
  git config sirius.worktreesDir (or foxpilot.worktreesDir, worktree.poolDir)
`);
}

export async function main(argv: string[] = process.argv.slice(2)): Promise<number> {
  const command = argv[0];
  const commandArgs = argv.slice(1);

  if (!command || command === "--help" || command === "-h" || command === "help") {
    printUsage(command ? console.log : console.error);
    return command ? 0 : 1;
  }

  if (command === "create") {
    if (commandArgs.includes("--help") || commandArgs.includes("-h")) {
      console.log(`Usage: worktree create <branch> [base-branch]

Create a new worktree for <branch> (optionally based on [base-branch]).

Arguments:
  <branch>       Name of the new worktree branch
  [base-branch]  Optional base branch or ref (defaults to repository HEAD/default)
`);
      return 0;
    }

    const { positionals } = parseArgs({
      args: commandArgs,
      options: {},
      allowPositionals: true,
    });

    const name = positionals[0];
    const base = positionals[1] ?? null;

    if (!name) {
      console.error("Error: Branch name required for create\n");
      console.error("Usage: worktree create <branch> [base-branch]");
      return 1;
    }

    const repoRoot = await getRepoRoot();
    const res = await createWorktree(name, base, repoRoot);
    console.log(JSON.stringify(res, null, 2));
    return res.status === "created" || res.status === "exists" ? 0 : 1;
  }

  if (command === "remove") {
    if (commandArgs.includes("--help") || commandArgs.includes("-h")) {
      console.log(`Usage: worktree remove <branch|path> [options]

Remove an existing worktree by branch name or path.

Arguments:
  <branch|path>        Branch name or path of the worktree to remove

Options:
  -f, --force          Force removal even if uncommitted changes exist
  -d, --delete-branch  Also delete the Git branch associated with the worktree
`);
      return 0;
    }

    const { values, positionals } = parseArgs({
      args: commandArgs,
      options: {
        force: { type: "boolean", short: "f", default: false },
        "delete-branch": { type: "boolean", short: "d", default: false },
      },
      allowPositionals: true,
    });

    const name = positionals[0];
    if (!name) {
      console.error("Error: Branch name or path required for remove\n");
      console.error("Usage: worktree remove <branch|path> [-f|--force] [-d|--delete-branch]");
      return 1;
    }

    const repoRoot = await getRepoRoot();
    const res = await removeWorktree(name, {
      force: values.force,
      deleteBranch: values["delete-branch"],
      repoRoot,
    });
    console.log(JSON.stringify(res, null, 2));
    return res.status === "removed" || res.status === "pruned" ? 0 : 1;
  }

  if (command === "list") {
    if (commandArgs.includes("--help") || commandArgs.includes("-h")) {
      console.log(`Usage: worktree list [options]

List all active worktrees across the repository.

Options:
  --json               Output worktree list in JSON format
`);
      return 0;
    }

    const { values } = parseArgs({
      args: commandArgs,
      options: {
        json: { type: "boolean", default: false },
      },
      allowPositionals: false,
    });

    const repoRoot = await getRepoRoot();
    const items = await listWorktrees(repoRoot);
    if (values.json) {
      console.log(JSON.stringify(items, null, 2));
    } else {
      console.log(`${"BRANCH".padEnd(35)} ${"HEAD".padEnd(12)} PATH`);
      console.log("-".repeat(80));
      for (const item of items) {
        const branch = (item.branch ?? "unknown").padEnd(35);
        const head = (item.head ?? "").slice(0, 10).padEnd(12);
        console.log(`${branch} ${head} ${item.path}`);
      }
    }
    return 0;
  }

  console.error(`Unknown command: ${command}\n`);
  printUsage(console.error);
  return 1;
}

if (import.meta.main) {
  main().then((code) => {
    process.exit(code);
  });
}
