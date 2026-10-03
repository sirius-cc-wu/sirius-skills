import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { existsSync } from "node:fs";
import {
  branchExists,
  createWorktree,
  getRepoRoot,
  getWorktreesDir,
  listWorktrees,
  main,
  removeWorktree,
  resolveWorktreesDir,
} from "../scripts/worktree";

describe("worktree", () => {
  let tempRepo: string;

  beforeEach(async () => {
    tempRepo = mkdtempSync(join(tmpdir(), "sirius-worktree-test-"));
    // Initialize git repo
    await Bun.$`git init -b main ${tempRepo}`.quiet();
    await Bun.$`git -C ${tempRepo} config user.name "Test User"`.quiet();
    await Bun.$`git -C ${tempRepo} config user.email "test@example.com"`.quiet();

    writeFileSync(join(tempRepo, "README.md"), "# Test Repo\n");
    await Bun.$`git -C ${tempRepo} add README.md`.quiet();
    await Bun.$`git -C ${tempRepo} commit -m "Initial commit"`.quiet();
  });

  afterEach(() => {
    if (tempRepo && existsSync(tempRepo)) {
      rmSync(tempRepo, { recursive: true, force: true });
    }
  });

  it("creates and lists worktree", async () => {
    const res = await createWorktree("feature-test", "main", tempRepo);
    expect(res.status).toBe("created");
    expect(existsSync(res.path)).toBe(true);
    expect(await branchExists("feature-test", tempRepo)).toBe(true);

    const items = await listWorktrees(tempRepo);
    const branches = items.map((i) => i.branch);
    expect(branches).toContain("feature-test");
  });

  it("handles creating existing worktree", async () => {
    const res1 = await createWorktree("dup-test", "main", tempRepo);
    expect(res1.status).toBe("created");

    const res2 = await createWorktree("dup-test", "main", tempRepo);
    expect(res2.status).toBe("exists");
  });

  it("removes worktree", async () => {
    const res = await createWorktree("rem-test", "main", tempRepo);
    expect(res.status).toBe("created");
    expect(existsSync(res.path)).toBe(true);

    const rem = await removeWorktree("rem-test", {
      force: true,
      deleteBranch: true,
      repoRoot: tempRepo,
    });
    expect(["removed", "pruned"]).toContain(rem.status);
    expect(existsSync(res.path)).toBe(false);
    expect(await branchExists("rem-test", tempRepo)).toBe(false);
  });

  it("detects worktrees directory via environment variables", async () => {
    const customPool = mkdtempSync(join(tmpdir(), "sirius-env-pool-"));
    try {
      process.env.SIRIUS_WORKTREES_DIR = customPool;
      expect(getWorktreesDir(tempRepo)).toBe(resolve(customPool));
      expect(await resolveWorktreesDir(tempRepo)).toBe(resolve(customPool));
      delete process.env.SIRIUS_WORKTREES_DIR;

      process.env.FOXPILOT_WORKTREES_DIR = customPool;
      expect(getWorktreesDir(tempRepo)).toBe(resolve(customPool));
      expect(await resolveWorktreesDir(tempRepo)).toBe(resolve(customPool));
      delete process.env.FOXPILOT_WORKTREES_DIR;

      process.env.WORKTREES_DIR = customPool;
      expect(getWorktreesDir(tempRepo)).toBe(resolve(customPool));
      expect(await resolveWorktreesDir(tempRepo)).toBe(resolve(customPool));
    } finally {
      delete process.env.SIRIUS_WORKTREES_DIR;
      delete process.env.FOXPILOT_WORKTREES_DIR;
      delete process.env.WORKTREES_DIR;
      if (existsSync(customPool)) {
        rmSync(customPool, { recursive: true, force: true });
      }
    }
  });

  it("detects worktrees directory via git config", async () => {
    const customPool = mkdtempSync(join(tmpdir(), "sirius-cfg-pool-"));
    try {
      await Bun.$`git -C ${tempRepo} config sirius.worktreesDir ${customPool}`.quiet();
      expect(getWorktreesDir(tempRepo)).toBe(resolve(customPool));
      expect(await resolveWorktreesDir(tempRepo)).toBe(resolve(customPool));

      const res = await createWorktree("cfg-branch", "main", tempRepo);
      expect(res.status).toBe("created");
      expect(res.path).toBe(join(customPool, "cfg-branch"));
      expect(existsSync(res.path)).toBe(true);
    } finally {
      if (existsSync(customPool)) {
        rmSync(customPool, { recursive: true, force: true });
      }
    }
  });

  it("detects worktrees directory via legacy git config foxpilot.worktreesDir", async () => {
    const customPool = mkdtempSync(join(tmpdir(), "foxpilot-cfg-pool-"));
    try {
      await Bun.$`git -C ${tempRepo} config foxpilot.worktreesDir ${customPool}`.quiet();
      expect(getWorktreesDir(tempRepo)).toBe(resolve(customPool));
      expect(await resolveWorktreesDir(tempRepo)).toBe(resolve(customPool));
    } finally {
      if (existsSync(customPool)) {
        rmSync(customPool, { recursive: true, force: true });
      }
    }
  });

  it("auto-detects existing worktree pool directory", async () => {
    const siblingPool = `${tempRepo}-sibling.worktrees`;
    const initialWtPath = join(siblingPool, "initial-wt");
    try {
      await Bun.$`git -C ${tempRepo} worktree add -b initial-wt ${initialWtPath}`.quiet();
      expect(getWorktreesDir(tempRepo)).toBe(resolve(siblingPool));
      expect(await resolveWorktreesDir(tempRepo)).toBe(resolve(siblingPool));

      const res = await createWorktree("second-wt", "main", tempRepo);
      expect(res.status).toBe("created");
      expect(res.path).toBe(join(siblingPool, "second-wt"));
      expect(existsSync(res.path)).toBe(true);
    } finally {
      if (existsSync(siblingPool)) {
        rmSync(siblingPool, { recursive: true, force: true });
      }
    }
  });

  it("removes worktree located outside default .worktrees directory", async () => {
    const customPool = mkdtempSync(join(tmpdir(), "sirius-custom-pool-"));
    const customWtPath = join(customPool, "outside-wt");
    try {
      await Bun.$`git -C ${tempRepo} worktree add -b outside-branch ${customWtPath}`.quiet();
      expect(existsSync(customWtPath)).toBe(true);

      const rem = await removeWorktree("outside-branch", {
        force: true,
        deleteBranch: true,
        repoRoot: tempRepo,
      });

      expect(["removed", "pruned"]).toContain(rem.status);
      expect(rem.path).toBe(resolve(customWtPath));
      expect(existsSync(customWtPath)).toBe(false);
      expect(await branchExists("outside-branch", tempRepo)).toBe(false);
    } finally {
      if (existsSync(customPool)) {
        rmSync(customPool, { recursive: true, force: true });
      }
    }
  });

  it("removes worktree by exact path and branch with slashes", async () => {
    const customPool = mkdtempSync(join(tmpdir(), "sirius-custom-pool-"));
    const customWtPath = join(customPool, "slash-wt");
    try {
      await Bun.$`git -C ${tempRepo} worktree add -b feature/slash-test ${customWtPath}`.quiet();
      expect(existsSync(customWtPath)).toBe(true);

      // Remove by exact path
      const rem = await removeWorktree(customWtPath, {
        force: true,
        deleteBranch: true,
        repoRoot: tempRepo,
      });

      expect(["removed", "pruned"]).toContain(rem.status);
      expect(rem.path).toBe(resolve(customWtPath));
      expect(existsSync(customWtPath)).toBe(false);
      expect(await branchExists("feature/slash-test", tempRepo)).toBe(false);
    } finally {
      if (existsSync(customPool)) {
        rmSync(customPool, { recursive: true, force: true });
      }
    }
  });

  it("supports bare repositories in getRepoRoot", async () => {
    const bareRepo = mkdtempSync(join(tmpdir(), "sirius-bare-test-"));
    try {
      await Bun.$`git init --bare ${bareRepo}`.quiet();
      const root = await getRepoRoot(bareRepo);
      expect(root).toBe(resolve(bareRepo));
    } finally {
      if (existsSync(bareRepo)) {
        rmSync(bareRepo, { recursive: true, force: true });
      }
    }
  });

  it("displays comprehensive usage on empty or help commands", async () => {
    expect(await main([])).toBe(1);
    expect(await main(["--help"])).toBe(0);
    expect(await main(["-h"])).toBe(0);
    expect(await main(["help"])).toBe(0);
    expect(await main(["create", "--help"])).toBe(0);
    expect(await main(["remove", "-h"])).toBe(0);
    expect(await main(["list", "--help"])).toBe(0);
    expect(await main(["unknown-cmd"])).toBe(1);
  });
});
