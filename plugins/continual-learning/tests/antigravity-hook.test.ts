import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { handleAntigravityStopHook } from "../src/antigravity-hook.ts";
import type { AntigravityStopHookInput } from "../src/types/antigravity.ts";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

describe("Antigravity CLI Stop Hook Adapter (Rule 4)", () => {
  it("Rule 4.1: clean stop on ineligible cadence returns { decision: 'allow' }", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "antigravity-test-"));
    try {
      const statePath = join(tempDir, "continual-learning.json");
      const input: AntigravityStopHookInput = {
        conversationId: "conv-1",
        workspacePaths: [tempDir],
        status: "completed",
        loopCount: 0,
      };

      // Turns = 1 (ineligible when minTurns = 10)
      const output = handleAntigravityStopHook(input, {
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

      assert.equal(output.decision, "allow");

      // Verify state was saved with incremented turns
      const saved = JSON.parse(readFileSync(statePath, "utf-8"));
      assert.equal(saved.turnsSinceLastRun, 1);
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it("Rule 4.2: followup trigger on eligible cadence returns { decision: 'continue', reason: ... }", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "antigravity-test-"));
    try {
      const statePath = join(tempDir, "continual-learning.json");
      const now = 1_000_000_000;
      const input: AntigravityStopHookInput = {
        conversationId: "conv-2",
        workspacePaths: [tempDir],
        status: "completed",
        loopCount: 0,
      };

      // Simulate state already having 9 turns and 150 minutes elapsed
      const initialSaved = {
        version: 1,
        lastRunAtMs: now - 150 * 60 * 1000,
        turnsSinceLastRun: 9,
        lastTranscriptMtimeMs: null,
        lastProcessedGenerationId: null,
        trialStartedAtMs: null,
      };
      writeFileSync(statePath, JSON.stringify(initialSaved), "utf-8");

      // Now adding 1 turn reaches 10 turns => cadence met!
      const output = handleAntigravityStopHook(input, {
        statePath,
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

      assert.equal(output.decision, "continue");
      assert.match(output.reason ?? "", /continual-learning/i);

      // Verify turns reset and lastRunAtMs recorded
      const saved = JSON.parse(readFileSync(statePath, "utf-8"));
      assert.equal(saved.turnsSinceLastRun, 0);
      assert.equal(saved.lastRunAtMs, now);
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it("Task 4.3: executes CLI process with stdin/stdout contract", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "antigravity-cli-test-"));
    try {
      const statePath = join(tempDir, "state.json");
      const input: AntigravityStopHookInput = {
        conversationId: "cli-conv-1",
        workspacePaths: [tempDir],
        status: "completed",
      };

      const hookScript = resolve(
        import.meta.dirname,
        "../src/antigravity-hook.ts"
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
      assert.equal(parsed.decision, "allow");
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });
});
