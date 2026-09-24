import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { handleCopilotSessionEndHook } from "../src/copilot-hook.ts";
import type { CopilotSessionEndInput } from "../src/types/copilot.ts";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

describe("Copilot CLI Adapter (Rule 5: Copilot CLI Lifecycle Hook Contract)", () => {
  const INITIAL_AGENTS_MD = `# Project Guidelines

## Core Rules
- Always use tabs for indentation in YAML
- Run lint before check-in
`;

  it("Rule 5.1: evaluates cadence against .copilot/state/continual-learning.json and exits cleanly when ineligible", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "copilot-test-ineligible-"));
    try {
      const statePath = join(tempDir, ".copilot/state/continual-learning.json");
      const input: CopilotSessionEndInput = {
        sessionId: "session-123",
        workspacePath: tempDir,
        status: "completed",
      };

      const output = handleCopilotSessionEndHook(input, {
        statePath,
        now: 1_000_000_000,
        config: {
          minTurns: 10,
          minMinutes: 120,
          trialMode: false,
          trialMinTurns: 3,
          trialMinMinutes: 15,
          trialDurationMinutes: 1440,
        },
      });

      assert.equal(output.status, "skipped");

      // Verify state was saved to .copilot/state/continual-learning.json with incremented turns
      const saved = JSON.parse(readFileSync(statePath, "utf-8"));
      assert.equal(saved.turnsSinceLastRun, 1);
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it("Rule 5.1 (Cadence Met): executes loop, creates index, patches AGENTS.md, and resets cadence", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "copilot-test-cadence-met-"));
    try {
      const statePath = join(tempDir, ".copilot/state/continual-learning.json");
      const indexPath = join(tempDir, ".copilot/state/continual-learning-index.json");
      const agentsPath = join(tempDir, "AGENTS.md");
      const now = 1_000_000_000;

      // 1. Create AGENTS.md on disk
      writeFileSync(agentsPath, INITIAL_AGENTS_MD, "utf-8");

      // 2. Create transcript with user correction and new fact
      const transcriptsDir = join(tempDir, ".copilot/transcripts");
      mkdirSync(transcriptsDir, { recursive: true });
      const transcriptPath = join(transcriptsDir, "session-456.jsonl");

      const transcriptContent = JSON.stringify({
        bulletsToUpdate: [
          {
            targetPattern: "use tabs for indentation in YAML",
            replacement: "- Always use 2 spaces for indentation in YAML",
          },
        ],
        bulletsToAdd: [
          {
            category: "Core Rules",
            bullet: "- Never commit directly to main branch",
          },
        ],
      });
      writeFileSync(transcriptPath, `${transcriptContent}\n`, "utf-8");

      // 3. Set initial state: 9 turns and 150 minutes elapsed => next turn triggers cadence
      mkdirSync(join(tempDir, ".copilot/state"), { recursive: true });
      writeFileSync(
        statePath,
        JSON.stringify({
          version: 1,
          lastRunAtMs: now - 150 * 60 * 1000,
          turnsSinceLastRun: 9,
          lastTranscriptMtimeMs: null,
          lastProcessedGenerationId: null,
          trialStartedAtMs: null,
        }),
        "utf-8"
      );

      const input: CopilotSessionEndInput = {
        sessionId: "session-456",
        workspacePath: tempDir,
        transcriptPath,
        status: "completed",
      };

      const output = handleCopilotSessionEndHook(input, {
        statePath,
        indexPath,
        agentsPath,
        now,
        config: {
          minTurns: 10,
          minMinutes: 120,
          trialMode: false,
          trialMinTurns: 3,
          trialMinMinutes: 15,
          trialDurationMinutes: 1440,
        },
      });

      assert.equal(output.status, "ok");

      // Verify state was reset and timestamp recorded
      const saved = JSON.parse(readFileSync(statePath, "utf-8"));
      assert.equal(saved.turnsSinceLastRun, 0);
      assert.equal(saved.lastRunAtMs, now);
      assert.equal(typeof saved.lastTranscriptMtimeMs, "number");
      assert.equal(saved.lastTranscriptMtimeMs > 0, true);

      // Verify observable disk side effect 1: continual-learning-index.json exists and tracks transcript
      assert.equal(existsSync(indexPath), true);
      const indexContent = JSON.parse(readFileSync(indexPath, "utf-8"));
      assert.equal(indexContent.version, 1);
      assert.equal(typeof indexContent.files[transcriptPath], "number");

      // Verify observable disk side effect 2: AGENTS.md was patched in-place
      const updatedAgents = readFileSync(agentsPath, "utf-8");
      assert.equal(
        updatedAgents.includes("- Always use 2 spaces for indentation in YAML"),
        true
      );
      assert.equal(
        updatedAgents.includes("- Always use tabs for indentation in YAML"),
        false
      );
      assert.equal(
        updatedAgents.includes("- Never commit directly to main branch"),
        true
      );
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it("executes CLI process with sessionEnd payload and produces disk side effects", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "copilot-cli-e2e-"));
    try {
      const statePath = join(tempDir, ".copilot/state/continual-learning.json");
      const indexPath = join(tempDir, ".copilot/state/continual-learning-index.json");
      const agentsPath = join(tempDir, "AGENTS.md");
      const now = Date.now();

      // Create initial AGENTS.md
      writeFileSync(agentsPath, INITIAL_AGENTS_MD, "utf-8");

      // Create transcript with correction
      const transcriptsDir = join(tempDir, ".copilot/transcripts");
      mkdirSync(transcriptsDir, { recursive: true });
      const transcriptPath = join(transcriptsDir, "cli-session.jsonl");

      const updateData = JSON.stringify({
        bulletsToUpdate: [
          {
            targetPattern: "tabs for indentation",
            replacement: "- Always use 2 spaces for indentation",
          },
        ],
        bulletsToAdd: [],
      });
      writeFileSync(transcriptPath, `${updateData}\n`, "utf-8");

      // Set initial state satisfied for cadence
      mkdirSync(join(tempDir, ".copilot/state"), { recursive: true });
      writeFileSync(
        statePath,
        JSON.stringify({
          version: 1,
          lastRunAtMs: now - 200 * 60 * 1000,
          turnsSinceLastRun: 15,
          lastTranscriptMtimeMs: null,
          lastProcessedGenerationId: null,
          trialStartedAtMs: null,
        }),
        "utf-8"
      );

      const input: CopilotSessionEndInput = {
        sessionId: "copilot-cli-sess",
        workspacePath: tempDir,
        transcriptPath,
        status: "completed",
      };

      const hookScript = resolve(
        import.meta.dirname,
        "../src/copilot-hook.ts"
      );

      const res = spawnSync(
        "node",
        ["--experimental-strip-types", hookScript],
        {
          input: JSON.stringify(input),
          encoding: "utf-8",
          env: {
            ...process.env,
            CONTINUAL_LEARNING_STATE_PATH: statePath,
          },
        }
      );

      assert.equal(res.status, 0);
      const parsed = JSON.parse(res.stdout.trim());
      assert.equal(parsed.status, "ok");

      // Verify observable disk side effects from the CLI execution
      assert.equal(existsSync(indexPath), true);
      const updatedAgents = readFileSync(agentsPath, "utf-8");
      assert.equal(
        updatedAgents.includes("- Always use 2 spaces for indentation"),
        true
      );
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });
});
