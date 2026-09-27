import type {
  CadenceConfig,
  CadenceResult,
  ContinuousLearningState,
} from "./types/common.ts";

/**
 * Pure evaluation of cadence gating according to Rule 1.
 * Determines if memory extraction should execute given current state, configuration, and time.
 */
export function evaluateCadence(
  state: ContinuousLearningState,
  config: CadenceConfig,
  currentMs: number
): CadenceResult {
  const trialDurationMs = config.trialDurationMinutes * 60 * 1000;
  const isTrialActive = Boolean(
    config.trialMode &&
      (state.trialStartedAtMs === null ||
        currentMs - state.trialStartedAtMs < trialDurationMs)
  );

  const effectiveMinTurns = isTrialActive
    ? config.trialMinTurns
    : config.minTurns;
  const effectiveMinMinutes = isTrialActive
    ? config.trialMinMinutes
    : config.minMinutes;

  const elapsedMinutes =
    state.lastRunAtMs > 0
      ? (currentMs - state.lastRunAtMs) / (60 * 1000)
      : Number.POSITIVE_INFINITY;

  const shouldRun =
    state.turnsSinceLastRun >= effectiveMinTurns &&
    elapsedMinutes >= effectiveMinMinutes;

  return {
    shouldRun,
    isTrialActive,
    effectiveMinTurns,
    effectiveMinMinutes,
    turnsSinceLastRun: state.turnsSinceLastRun,
    elapsedMinutes,
  };
}
