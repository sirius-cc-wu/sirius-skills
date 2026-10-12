import { describe, it, expect, beforeEach, afterEach } from "bun:test";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, realpathSync, rmSync, writeFileSync } from "node:fs";
import { cpus, tmpdir } from "node:os";
import { join, resolve } from "node:path";
import {
  branchExists,
  createWorktree,
  ensureCargoPoolConfig,
  getDiskInfo,
  getRepoRoot,
  getWorktreesDir,
  listWorktrees,
  main,
  removeWorktree,
  resolveWorktreesDir,
} from "../scripts/worktree";

describe("worktree", () => {
  let tempRepo: string;

  interface RunMainOptions {
    cwd: string;
    args: string[];
    env?: Record<string, string>;
  }

  async function runMainIsolated(options: RunMainOptions): Promise<{
    exitCode: number;
    stdout: string[];
    stderr: string[];
  }> {
    const originalCwd = process.cwd();
    const originalEnv = {
      CARGO_TARGET_DIR: process.env.CARGO_TARGET_DIR,
      CARGO_BUILD_TARGET_DIR: process.env.CARGO_BUILD_TARGET_DIR,
      CARGO_BUILD_BUILD_DIR: process.env.CARGO_BUILD_BUILD_DIR,
    };
    delete process.env.CARGO_TARGET_DIR;
    delete process.env.CARGO_BUILD_TARGET_DIR;
    delete process.env.CARGO_BUILD_BUILD_DIR;

    if (options.env) {
      for (const [k, v] of Object.entries(options.env)) {
        process.env[k] = v;
      }
    }

    const stdout: string[] = [];
    const stderr: string[] = [];
    const originalLog = console.log;
    const originalError = console.error;
    console.log = (...args: any[]) => {
      stdout.push(args.map(String).join(" "));
    };
    console.error = (...args: any[]) => {
      stderr.push(args.map(String).join(" "));
    };

    try {
      process.chdir(options.cwd);
      const exitCode = await main(options.args);
      return { exitCode, stdout, stderr };
    } finally {
      process.chdir(originalCwd);
      console.log = originalLog;
      console.error = originalError;
      delete process.env.CARGO_TARGET_DIR;
      delete process.env.CARGO_BUILD_TARGET_DIR;
      delete process.env.CARGO_BUILD_BUILD_DIR;
      if (originalEnv.CARGO_TARGET_DIR !== undefined) {
        process.env.CARGO_TARGET_DIR = originalEnv.CARGO_TARGET_DIR;
      }
      if (originalEnv.CARGO_BUILD_TARGET_DIR !== undefined) {
        process.env.CARGO_BUILD_TARGET_DIR = originalEnv.CARGO_BUILD_TARGET_DIR;
      }
      if (originalEnv.CARGO_BUILD_BUILD_DIR !== undefined) {
        process.env.CARGO_BUILD_BUILD_DIR = originalEnv.CARGO_BUILD_BUILD_DIR;
      }
    }
  }

  let savedEnvVars: {
    WORKTREES_DIR?: string;
    SIRIUS_WORKTREES_DIR?: string;
    FOXPILOT_WORKTREES_DIR?: string;
  };

  beforeEach(async () => {
    savedEnvVars = {
      WORKTREES_DIR: process.env.WORKTREES_DIR,
      SIRIUS_WORKTREES_DIR: process.env.SIRIUS_WORKTREES_DIR,
      FOXPILOT_WORKTREES_DIR: process.env.FOXPILOT_WORKTREES_DIR,
    };
    delete process.env.WORKTREES_DIR;
    delete process.env.SIRIUS_WORKTREES_DIR;
    delete process.env.FOXPILOT_WORKTREES_DIR;

    tempRepo = realpathSync(mkdtempSync(join(tmpdir(), "sirius-worktree-test-")));
    // Initialize git repo
    await Bun.$`git init -b main ${tempRepo}`.quiet();
    await Bun.$`git -C ${tempRepo} config user.name "Test User"`.quiet();
    await Bun.$`git -C ${tempRepo} config user.email "test@example.com"`.quiet();

    writeFileSync(join(tempRepo, "README.md"), "# Test Repo\n");
    await Bun.$`git -C ${tempRepo} add README.md`.quiet();
    await Bun.$`git -C ${tempRepo} commit -m "Initial commit"`.quiet();
  });

  afterEach(() => {
    if (savedEnvVars) {
      if (savedEnvVars.WORKTREES_DIR !== undefined) {
        process.env.WORKTREES_DIR = savedEnvVars.WORKTREES_DIR;
      } else {
        delete process.env.WORKTREES_DIR;
      }
      if (savedEnvVars.SIRIUS_WORKTREES_DIR !== undefined) {
        process.env.SIRIUS_WORKTREES_DIR = savedEnvVars.SIRIUS_WORKTREES_DIR;
      } else {
        delete process.env.SIRIUS_WORKTREES_DIR;
      }
      if (savedEnvVars.FOXPILOT_WORKTREES_DIR !== undefined) {
        process.env.FOXPILOT_WORKTREES_DIR = savedEnvVars.FOXPILOT_WORKTREES_DIR;
      } else {
        delete process.env.FOXPILOT_WORKTREES_DIR;
      }
    }
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
    const origLog = console.log;
    const origErr = console.error;
    console.log = () => {};
    console.error = () => {};
    try {
      expect(await main([])).toBe(1);
      expect(await main(["--help"])).toBe(0);
      expect(await main(["-h"])).toBe(0);
      expect(await main(["help"])).toBe(0);
      expect(await main(["create", "--help"])).toBe(0);
      expect(await main(["remove", "-h"])).toBe(0);
      expect(await main(["list", "--help"])).toBe(0);
      expect(await main(["unknown-cmd"])).toBe(1);
    } finally {
      console.log = origLog;
      console.error = origErr;
    }
  });

  it("writes pool cargo config with jobs and without target-dir", async () => {
    writeFileSync(join(tempRepo, "Cargo.toml"), '[package]\nname = "test"\nversion = "0.1.0"\n');
    const worktreesDir = await resolveWorktreesDir(tempRepo);
    const cargoConfig = join(worktreesDir, ".cargo", "config.toml");
    expect(existsSync(cargoConfig)).toBe(true);
    const content = readFileSync(cargoConfig, "utf-8");
    expect(content).toContain(
      "# Generated by worktree.ts for Cargo concurrency hygiene. Each worktree keeps its own target/ directory."
    );
    expect(content).toContain("[build]");
    expect(content).toContain("jobs =");
    expect(content).not.toContain("target-dir");
    expect(content).not.toContain("build-dir");
  });

  it("migrates legacy pool config and keeps jobs and user keys", async () => {
    const legacyFirstLine =
      "# Generated by worktree.ts for automatic shared target cache & concurrency hygiene\r\n";
    const legacyContent =
      legacyFirstLine +
      "[build]\r\n" +
      'target-dir = "/path/to/shared/target"\r\n' +
      "jobs = 6\r\n" +
      "\r\n" +
      "[env]\r\n" +
      'CUSTOM_VAR = "hello"\r\n';

    const worktreesDir = join(tempRepo, ".worktrees");
    const cargoDir = join(worktreesDir, ".cargo");
    mkdirSync(cargoDir, { recursive: true });
    const cargoConfig = join(cargoDir, "config.toml");
    writeFileSync(cargoConfig, legacyContent, "utf-8");
    writeFileSync(join(tempRepo, "Cargo.toml"), '[package]\nname = "test"\nversion = "0.1.0"\n');

    const stderrMessages: string[] = [];
    const originalConsoleError = console.error;
    console.error = (msg: string) => {
      stderrMessages.push(msg);
    };
    try {
      const result = ensureCargoPoolConfig(tempRepo, worktreesDir);
      expect(result).toBe(true);
      const updatedContent = readFileSync(cargoConfig, "utf-8");
      expect(updatedContent).toBe(
        "# Generated by worktree.ts for Cargo concurrency hygiene. Each worktree keeps its own target/ directory.\r\n" +
          "[build]\r\n" +
          "jobs = 6\r\n" +
          "\r\n" +
          "[env]\r\n" +
          'CUSTOM_VAR = "hello"\r\n'
      );
      expect(stderrMessages.length).toBe(1);
      expect(stderrMessages[0]).toBe(
        `worktree: removed shared target-dir from ${cargoConfig}; each worktree now uses its own target/`
      );
    } finally {
      console.error = originalConsoleError;
    }
  });

  it("legacy migration is idempotent", async () => {
    const legacyContent =
      "# Generated by worktree.ts for automatic shared target cache & concurrency hygiene\n" +
      "[build]\n" +
      'target-dir = "/path/to/shared/target"\n' +
      "jobs = 4\n";
    const worktreesDir = join(tempRepo, ".worktrees");
    const cargoDir = join(worktreesDir, ".cargo");
    mkdirSync(cargoDir, { recursive: true });
    const cargoConfig = join(cargoDir, "config.toml");
    writeFileSync(cargoConfig, legacyContent, "utf-8");
    writeFileSync(join(tempRepo, "Cargo.toml"), '[package]\nname = "test"\nversion = "0.1.0"\n');

    const originalConsoleError = console.error;
    console.error = () => {};
    try {
      const res1 = ensureCargoPoolConfig(tempRepo, worktreesDir);
      expect(res1).toBe(true);
      const contentAfterFirst = readFileSync(cargoConfig, "utf-8");

      const res2 = ensureCargoPoolConfig(tempRepo, worktreesDir);
      expect(res2).toBe(false);
      const contentAfterSecond = readFileSync(cargoConfig, "utf-8");
      expect(contentAfterSecond).toBe(contentAfterFirst);
    } finally {
      console.error = originalConsoleError;
    }
  });

  it("does not modify user-authored pool config that sets target-dir", async () => {
    const userContent =
      "# My custom cargo configuration\n" +
      "[build]\n" +
      'target-dir = "/custom/target"\n' +
      "jobs = 2\n";
    const worktreesDir = join(tempRepo, ".worktrees");
    const cargoDir = join(worktreesDir, ".cargo");
    mkdirSync(cargoDir, { recursive: true });
    const cargoConfig = join(cargoDir, "config.toml");
    writeFileSync(cargoConfig, userContent, "utf-8");
    writeFileSync(join(tempRepo, "Cargo.toml"), '[package]\nname = "test"\nversion = "0.1.0"\n');

    const res = ensureCargoPoolConfig(tempRepo, worktreesDir);
    expect(res).toBe(false);
    const contentAfter = readFileSync(cargoConfig, "utf-8");
    expect(contentAfter).toBe(userContent);
  });

  it("hygiene reports shared target from user-authored pool config", async () => {
    const userContent =
      "# User authored config\n" +
      "[build]\n" +
      'target-dir = "/custom/shared/target"\n' +
      "jobs = 4\n";
    const worktreesDir = join(tempRepo, ".worktrees");
    const cargoDir = join(worktreesDir, ".cargo");
    mkdirSync(cargoDir, { recursive: true });
    const cargoConfig = join(cargoDir, "config.toml");
    writeFileSync(cargoConfig, userContent, "utf-8");
    writeFileSync(join(tempRepo, "Cargo.toml"), '[package]\nname = "test"\nversion = "0.1.0"\n');

    const { exitCode, stdout } = await runMainIsolated({
      cwd: tempRepo,
      args: ["hygiene"],
    });

    expect(exitCode).toBe(0);
    const output = stdout.join("\n");
    expect(output).toContain("Cargo Target Isolation: shared");
    const realConfigPath = realpathSync(cargoConfig);
    expect(output.includes(cargoConfig) || output.includes(realConfigPath)).toBe(true);
    expect(output).toContain(
      "Shared Cargo build output lets one checkout reuse stale artifacts of another."
    );
  });

  it("hygiene reports dotted build.target-dir in pool config", async () => {
    const userContent =
      "# User authored config with dotted key\n" +
      'build.target-dir = "/custom/dotted/target"\n' +
      "build.jobs = 4\n";
    const worktreesDir = join(tempRepo, ".worktrees");
    const cargoDir = join(worktreesDir, ".cargo");
    mkdirSync(cargoDir, { recursive: true });
    const cargoConfig = join(cargoDir, "config.toml");
    writeFileSync(cargoConfig, userContent, "utf-8");
    writeFileSync(join(tempRepo, "Cargo.toml"), '[package]\nname = "test"\nversion = "0.1.0"\n');

    const { exitCode, stdout } = await runMainIsolated({
      cwd: tempRepo,
      args: ["hygiene"],
    });

    expect(exitCode).toBe(0);
    const output = stdout.join("\n");
    expect(output).toContain("Cargo Target Isolation: shared");
    const realConfigPath = realpathSync(cargoConfig);
    expect(output.includes(cargoConfig) || output.includes(realConfigPath)).toBe(true);
    expect(output).toContain(
      "Shared Cargo build output lets one checkout reuse stale artifacts of another."
    );
  });

  it("hygiene reports CARGO_TARGET_DIR override", async () => {
    writeFileSync(join(tempRepo, "Cargo.toml"), '[package]\nname = "test"\nversion = "0.1.0"\n');

    const overridePath = "/tmp/shared-cargo-target";
    const { exitCode, stdout } = await runMainIsolated({
      cwd: tempRepo,
      args: ["hygiene"],
      env: { CARGO_TARGET_DIR: overridePath },
    });

    expect(exitCode).toBe(0);
    const output = stdout.join("\n");
    expect(output).toContain("Cargo Target Isolation: shared");
    expect(output).toContain(`CARGO_TARGET_DIR=${overridePath}`);
    expect(output).toContain(
      "Shared Cargo build output lets one checkout reuse stale artifacts of another."
    );
  });

  it("hygiene reports isolated when no override exists", async () => {
    writeFileSync(join(tempRepo, "Cargo.toml"), '[package]\nname = "test"\nversion = "0.1.0"\n');

    const { exitCode, stdout } = await runMainIsolated({
      cwd: tempRepo,
      args: ["hygiene"],
    });

    expect(exitCode).toBe(0);
    const output = stdout.join("\n");
    expect(output).toContain("Cargo Target Isolation: isolated (checked: pool config, environment)");
    expect(output).not.toContain("Cargo Target Isolation: shared");
  });

  it("hygiene reports target size for main checkout and worktree", async () => {
    writeFileSync(join(tempRepo, "Cargo.toml"), '[package]\nname = "test"\nversion = "0.1.0"\n');
    const wtRes = await createWorktree("size-wt", "main", tempRepo);
    expect(wtRes.status).toBe("created");

    const noTargetWt = await createWorktree("no-target-wt", "main", tempRepo);
    expect(noTargetWt.status).toBe("created");

    const mainTarget = join(tempRepo, "target");
    mkdirSync(mainTarget, { recursive: true });
    writeFileSync(join(mainTarget, "dummy-artifact.bin"), "main build output artifact");

    const wtTarget = join(wtRes.path, "target");
    mkdirSync(wtTarget, { recursive: true });
    writeFileSync(join(wtTarget, "dummy-artifact.bin"), "worktree build output artifact");

    const { exitCode, stdout } = await runMainIsolated({
      cwd: tempRepo,
      args: ["hygiene"],
    });

    expect(exitCode).toBe(0);
    const output = stdout.join("\n");
    expect(output).toContain("Cargo Target Sizes:");
    expect(output).toMatch(/\(main\): \d+\.\d GB/);
    expect(output).toMatch(/size-wt: \d+\.\d GB/);
    expect(output).toMatch(/Total: \d+\.\d GB/);
    expect(output).not.toContain("no-target-wt");
  });

  it("hygiene labels main checkout when run from a linked worktree", async () => {
    const wtRes = await createWorktree("linked-label-wt", "main", tempRepo);
    expect(wtRes.status).toBe("created");

    const mainTarget = join(tempRepo, "target");
    mkdirSync(mainTarget, { recursive: true });
    writeFileSync(join(mainTarget, "dummy-artifact.bin"), "main target artifact");

    const wtTarget = join(wtRes.path, "target");
    mkdirSync(wtTarget, { recursive: true });
    writeFileSync(join(wtTarget, "dummy-artifact.bin"), "linked target artifact");

    const { exitCode, stdout } = await runMainIsolated({
      cwd: wtRes.path,
      args: ["hygiene"],
    });

    expect(exitCode).toBe(0);
    const output = stdout.join("\n");
    expect(output).toContain("Cargo Target Sizes:");
    const sizesIndex = stdout.indexOf("Cargo Target Sizes:");
    expect(sizesIndex).toBeGreaterThan(-1);
    expect(stdout[sizesIndex + 1]).toMatch(/^\s*\(main\): \d+\.\d GB$/);
    expect(stdout[sizesIndex + 2]).toMatch(/^\s*linked-label-wt: \d+\.\d GB$/);
    expect(stdout[sizesIndex + 3]).toMatch(/^\s*Total: \d+\.\d GB$/);
    expect(stdout.some((line) => /^\s*main:/.test(line))).toBe(false);
  });

  it("env prints jobs and unsets target overrides without a path", async () => {
    const { exitCode, stdout } = await runMainIsolated({
      cwd: tempRepo,
      args: ["env", "2"],
    });

    expect(exitCode).toBe(0);
    const cpuCount = cpus().length || 4;
    const expectedJobs = Math.max(1, Math.floor(cpuCount / 2));
    expect(stdout).toEqual([
      `export CARGO_BUILD_JOBS=${expectedJobs}`,
      "unset CARGO_TARGET_DIR CARGO_BUILD_TARGET_DIR CARGO_BUILD_BUILD_DIR",
    ]);
  });

  it("retrieves disk space information for existing directory", async () => {
    const disk = await getDiskInfo(tempRepo);
    expect(disk).not.toBeNull();
    if (disk) {
      expect(disk.totalGb).toBeGreaterThan(0);
      expect(disk.availableGb).toBeGreaterThan(0);
      expect(disk.capacityPercent).toBeGreaterThanOrEqual(0);
      expect(disk.capacityPercent).toBeLessThanOrEqual(100);
    }
  });

  it("fails worktree creation when required disk space exceeds available space", async () => {
    const res = await createWorktree("disk-fail-test", "main", tempRepo, {
      minDiskGb: 999999, // Impossibly large requirement
    });
    expect(res.status).toBe("error");
    expect(res.error).toContain("Pre-flight disk check failed");
  });

  it("removes local target directory during worktree removal", async () => {
    const res = await createWorktree("target-clean-test", "main", tempRepo);
    expect(res.status).toBe("created");
    const localTarget = join(res.path, "target");
    mkdirSync(localTarget, { recursive: true });
    writeFileSync(join(localTarget, "dummy.o"), "dummy");
    expect(existsSync(localTarget)).toBe(true);

    const rem = await removeWorktree("target-clean-test", { repoRoot: tempRepo });
    expect(rem.status).toBe("removed");
    expect(existsSync(res.path)).toBe(false);
  });

  it("executes hygiene and env commands successfully", async () => {
    const resHygiene = await runMainIsolated({
      cwd: tempRepo,
      args: ["hygiene"],
    });
    expect(resHygiene.exitCode).toBe(0);

    const resEnv = await runMainIsolated({
      cwd: tempRepo,
      args: ["env", "2"],
    });
    expect(resEnv.exitCode).toBe(0);
  });
});
