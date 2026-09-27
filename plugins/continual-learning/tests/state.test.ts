import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  loadCadenceConfigFromEnv,
  loadState,
  saveState,
  parsePositiveInt,
  parseBoolean,
} from "../src/state.ts";
import { INITIAL_STATE, DEFAULT_CADENCE_CONFIG } from "../src/types/common.ts";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

describe("State and Configuration Management (src/state.ts)", () => {
  it("parsePositiveInt handles valid, zero, negative, and missing inputs", () => {
    assert.equal(parsePositiveInt("42", 10), 42);
    assert.equal(parsePositiveInt("0", 10), 10);
    assert.equal(parsePositiveInt("-5", 10), 10);
    assert.equal(parsePositiveInt(undefined, 10), 10);
    assert.equal(parsePositiveInt("not-a-number", 10), 10);
  });

  it("parseBoolean correctly parses true/false string variants", () => {
    assert.equal(parseBoolean("true"), true);
    assert.equal(parseBoolean("1"), true);
    assert.equal(parseBoolean("yes"), true);
    assert.equal(parseBoolean("on"), true);
    assert.equal(parseBoolean("false"), false);
    assert.equal(parseBoolean("0"), false);
    assert.equal(parseBoolean(undefined), false);
  });

  it("loadCadenceConfigFromEnv loads defaults when env vars are unset", () => {
    const originalEnv = { ...process.env };
    try {
      delete process.env.CONTINUAL_LEARNING_MIN_TURNS;
      delete process.env.CONTINUAL_LEARNING_MIN_MINUTES;
      delete process.env.CONTINUAL_LEARNING_TRIAL_MODE;

      const config = loadCadenceConfigFromEnv();
      assert.equal(config.minTurns, DEFAULT_CADENCE_CONFIG.minTurns);
      assert.equal(config.minMinutes, DEFAULT_CADENCE_CONFIG.minMinutes);
      assert.equal(config.trialMode, false);
    } finally {
      process.env = originalEnv;
    }
  });

  it("loadCadenceConfigFromEnv respects environment variables", () => {
    const originalEnv = { ...process.env };
    try {
      process.env.CONTINUAL_LEARNING_MIN_TURNS = "5";
      process.env.CONTINUAL_LEARNING_MIN_MINUTES = "60";
      process.env.CONTINUAL_LEARNING_TRIAL_MODE = "true";
      process.env.CONTINUAL_LEARNING_TRIAL_MIN_TURNS = "2";
      process.env.CONTINUAL_LEARNING_TRIAL_MIN_MINUTES = "10";
      process.env.CONTINUAL_LEARNING_TRIAL_DURATION_MINUTES = "300";

      const config = loadCadenceConfigFromEnv();
      assert.equal(config.minTurns, 5);
      assert.equal(config.minMinutes, 60);
      assert.equal(config.trialMode, true);
      assert.equal(config.trialMinTurns, 2);
      assert.equal(config.trialMinMinutes, 10);
      assert.equal(config.trialDurationMinutes, 300);
    } finally {
      process.env = originalEnv;
    }
  });

  it("loadState returns INITIAL_STATE if file does not exist or has wrong version", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "state-test-"));
    try {
      const missingPath = join(tempDir, "missing.json");
      assert.deepEqual(loadState(missingPath), INITIAL_STATE);

      const invalidVersionPath = join(tempDir, "invalid-version.json");
      writeFileSync(invalidVersionPath, JSON.stringify({ version: 99 }), "utf-8");
      assert.deepEqual(loadState(invalidVersionPath), INITIAL_STATE);

      const corruptedPath = join(tempDir, "corrupted.json");
      writeFileSync(corruptedPath, "{ not valid json", "utf-8");
      assert.deepEqual(loadState(corruptedPath), INITIAL_STATE);
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it("saveState and loadState persist and read state accurately", () => {
    const tempDir = mkdtempSync(join(tmpdir(), "state-test-"));
    try {
      const statePath = join(tempDir, "nested", "state.json");
      const stateToSave = {
        version: 1 as const,
        lastRunAtMs: 123456789,
        turnsSinceLastRun: 7,
        lastTranscriptMtimeMs: 987654321,
        lastProcessedGenerationId: "gen-abc",
        trialStartedAtMs: 111222333,
      };

      saveState(statePath, stateToSave);

      const raw = readFileSync(statePath, "utf-8");
      const parsed = JSON.parse(raw);
      assert.equal(parsed.turnsSinceLastRun, 7);

      const loaded = loadState(statePath);
      assert.deepEqual(loaded, stateToSave);
    } finally {
      rmSync(tempDir, { recursive: true, force: true });
    }
  });
});
