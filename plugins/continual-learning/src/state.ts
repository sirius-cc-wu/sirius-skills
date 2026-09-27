import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import {
  DEFAULT_CADENCE_CONFIG,
  INITIAL_STATE,
  type CadenceConfig,
  type ContinuousLearningState,
} from "./types/common.ts";

export interface HookExecutionOptions {
  statePath?: string;
  now?: number;
  config?: CadenceConfig;
}

export function parsePositiveInt(value: string | undefined, fallback: number): number {
  if (!value) return fallback;
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

export function parseBoolean(value: string | undefined): boolean {
  if (!value) return false;
  const normalized = value.trim().toLowerCase();
  return (
    normalized === "1" ||
    normalized === "true" ||
    normalized === "yes" ||
    normalized === "on"
  );
}

export function loadCadenceConfigFromEnv(): CadenceConfig {
  const env = process.env;
  return {
    minTurns: parsePositiveInt(
      env.CONTINUAL_LEARNING_MIN_TURNS ?? env.CONTINUOUS_LEARNING_MIN_TURNS,
      DEFAULT_CADENCE_CONFIG.minTurns
    ),
    minMinutes: parsePositiveInt(
      env.CONTINUAL_LEARNING_MIN_MINUTES ?? env.CONTINUOUS_LEARNING_MIN_MINUTES,
      DEFAULT_CADENCE_CONFIG.minMinutes
    ),
    trialMode: parseBoolean(
      env.CONTINUAL_LEARNING_TRIAL_MODE ?? env.CONTINUOUS_LEARNING_TRIAL_MODE
    ),
    trialMinTurns: parsePositiveInt(
      env.CONTINUAL_LEARNING_TRIAL_MIN_TURNS ?? env.CONTINUOUS_LEARNING_TRIAL_MIN_TURNS,
      DEFAULT_CADENCE_CONFIG.trialMinTurns
    ),
    trialMinMinutes: parsePositiveInt(
      env.CONTINUAL_LEARNING_TRIAL_MIN_MINUTES ?? env.CONTINUOUS_LEARNING_TRIAL_MIN_MINUTES,
      DEFAULT_CADENCE_CONFIG.trialMinMinutes
    ),
    trialDurationMinutes: parsePositiveInt(
      env.CONTINUAL_LEARNING_TRIAL_DURATION_MINUTES ?? env.CONTINUOUS_LEARNING_TRIAL_DURATION_MINUTES,
      DEFAULT_CADENCE_CONFIG.trialDurationMinutes
    ),
  };
}

export function loadState(statePath: string): ContinuousLearningState {
  if (!existsSync(statePath)) {
    return { ...INITIAL_STATE };
  }
  try {
    const raw = readFileSync(statePath, "utf-8");
    const parsed = JSON.parse(raw) as Partial<ContinuousLearningState>;
    if (parsed.version !== 1) {
      return { ...INITIAL_STATE };
    }
    return {
      version: 1,
      lastRunAtMs: typeof parsed.lastRunAtMs === "number" ? parsed.lastRunAtMs : 0,
      turnsSinceLastRun:
        typeof parsed.turnsSinceLastRun === "number" && parsed.turnsSinceLastRun >= 0
          ? parsed.turnsSinceLastRun
          : 0,
      lastTranscriptMtimeMs:
        typeof parsed.lastTranscriptMtimeMs === "number"
          ? parsed.lastTranscriptMtimeMs
          : null,
      lastProcessedGenerationId:
        typeof parsed.lastProcessedGenerationId === "string"
          ? parsed.lastProcessedGenerationId
          : null,
      trialStartedAtMs:
        typeof parsed.trialStartedAtMs === "number" ? parsed.trialStartedAtMs : null,
    };
  } catch {
    return { ...INITIAL_STATE };
  }
}

export function saveState(statePath: string, state: ContinuousLearningState): void {
  const dir = dirname(statePath);
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true });
  }
  writeFileSync(statePath, `${JSON.stringify(state, null, 2)}\n`, "utf-8");
}
