import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { evaluateCadence } from "../src/cadence.ts";
import {
  DEFAULT_CADENCE_CONFIG,
  type CadenceConfig,
  type ContinuousLearningState,
} from "../src/types/common.ts";

describe("Cadence Engine (Rule 1: Cadence Gating)", () => {
  it("Rule 1.1: insufficient turns does not trigger learning", () => {
    const now = 1_000_000_000;
    const elapsedMinutes = 150;
    const lastRunAtMs = now - elapsedMinutes * 60 * 1000;

    const state: ContinuousLearningState = {
      version: 1,
      lastRunAtMs,
      turnsSinceLastRun: 4,
      lastTranscriptMtimeMs: null,
      lastProcessedGenerationId: null,
      trialStartedAtMs: null,
    };

    const config: CadenceConfig = {
      ...DEFAULT_CADENCE_CONFIG,
      minTurns: 10,
      minMinutes: 120,
    };

    const result = evaluateCadence(state, config, now);

    assert.equal(result.shouldRun, false);
    assert.equal(result.isTrialActive, false);
    assert.equal(result.effectiveMinTurns, 10);
    assert.equal(result.effectiveMinMinutes, 120);
    assert.equal(result.turnsSinceLastRun, 4);
  });

  it("Rule 1.2: cadence met triggers learning", () => {
    const now = 1_000_000_000;
    const elapsedMinutes = 130;
    const lastRunAtMs = now - elapsedMinutes * 60 * 1000;

    const state: ContinuousLearningState = {
      version: 1,
      lastRunAtMs,
      turnsSinceLastRun: 12,
      lastTranscriptMtimeMs: null,
      lastProcessedGenerationId: null,
      trialStartedAtMs: null,
    };

    const config: CadenceConfig = {
      ...DEFAULT_CADENCE_CONFIG,
      minTurns: 10,
      minMinutes: 120,
    };

    const result = evaluateCadence(state, config, now);

    assert.equal(result.shouldRun, true);
    assert.equal(result.isTrialActive, false);
    assert.equal(result.effectiveMinTurns, 10);
    assert.equal(result.effectiveMinMinutes, 120);
    assert.equal(result.turnsSinceLastRun, 12);
  });

  it("Rule 1.3: trial mode active governs thresholds and triggers learning", () => {
    const now = 1_000_000_000;
    const trialStartedAtMs = now - 2 * 60 * 60 * 1000; // 2 hours ago (< 24h)
    const elapsedMinutes = 20;
    const lastRunAtMs = now - elapsedMinutes * 60 * 1000;

    const state: ContinuousLearningState = {
      version: 1,
      lastRunAtMs,
      turnsSinceLastRun: 4,
      lastTranscriptMtimeMs: null,
      lastProcessedGenerationId: null,
      trialStartedAtMs,
    };

    const config: CadenceConfig = {
      ...DEFAULT_CADENCE_CONFIG,
      trialMode: true,
      trialMinTurns: 3,
      trialMinMinutes: 15,
      trialDurationMinutes: 24 * 60,
    };

    const result = evaluateCadence(state, config, now);

    assert.equal(result.shouldRun, true);
    assert.equal(result.isTrialActive, true);
    assert.equal(result.effectiveMinTurns, 3);
    assert.equal(result.effectiveMinMinutes, 15);
  });

  it("Rule 1.4: expired trial automatically reverts to default thresholds", () => {
    const now = 1_000_000_000;
    const trialStartedAtMs = now - 25 * 60 * 60 * 1000; // 25 hours ago (> 24h)
    const elapsedMinutes = 20;
    const lastRunAtMs = now - elapsedMinutes * 60 * 1000;

    const state: ContinuousLearningState = {
      version: 1,
      lastRunAtMs,
      turnsSinceLastRun: 4,
      lastTranscriptMtimeMs: null,
      lastProcessedGenerationId: null,
      trialStartedAtMs,
    };

    const config: CadenceConfig = {
      ...DEFAULT_CADENCE_CONFIG,
      minTurns: 10,
      minMinutes: 120,
      trialMode: true,
      trialMinTurns: 3,
      trialMinMinutes: 15,
      trialDurationMinutes: 24 * 60,
    };

    const result = evaluateCadence(state, config, now);

    // Reverts to default: minTurns = 10, minMinutes = 120
    // With turns = 4 and elapsedMinutes = 20, learning should not trigger
    assert.equal(result.shouldRun, false);
    assert.equal(result.isTrialActive, false);
    assert.equal(result.effectiveMinTurns, 10);
    assert.equal(result.effectiveMinMinutes, 120);
  });

  it("handles initial state (lastRunAtMs = 0) with sufficient turns", () => {
    const now = 1_000_000_000;
    const state: ContinuousLearningState = {
      version: 1,
      lastRunAtMs: 0,
      turnsSinceLastRun: 10,
      lastTranscriptMtimeMs: null,
      lastProcessedGenerationId: null,
      trialStartedAtMs: null,
    };

    const result = evaluateCadence(state, DEFAULT_CADENCE_CONFIG, now);

    assert.equal(result.shouldRun, true);
  });
});
