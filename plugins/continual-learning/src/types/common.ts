export interface ContinuousLearningState {
  version: 1;
  lastRunAtMs: number;
  turnsSinceLastRun: number;
  lastTranscriptMtimeMs: number | null;
  lastProcessedGenerationId: string | null;
  trialStartedAtMs: number | null;
}

export interface CadenceConfig {
  minTurns: number;
  minMinutes: number;
  trialMode: boolean;
  trialMinTurns: number;
  trialMinMinutes: number;
  trialDurationMinutes: number;
}

export interface CadenceResult {
  shouldRun: boolean;
  isTrialActive: boolean;
  effectiveMinTurns: number;
  effectiveMinMinutes: number;
  turnsSinceLastRun: number;
  elapsedMinutes: number;
}

export interface TranscriptIndex {
  version: 1;
  files: Record<string, number>;
}

export interface BulletUpdate {
  targetPattern: RegExp | string;
  replacement: string;
}

export interface BulletAdd {
  category?: string;
  bullet: string;
}

export interface PatchResult {
  modified: boolean;
  message: string;
  updatedContent?: string;
}

export const DEFAULT_CADENCE_CONFIG: CadenceConfig = {
  minTurns: 10,
  minMinutes: 120,
  trialMode: false,
  trialMinTurns: 3,
  trialMinMinutes: 15,
  trialDurationMinutes: 24 * 60,
};

export const INITIAL_STATE: ContinuousLearningState = {
  version: 1,
  lastRunAtMs: 0,
  turnsSinceLastRun: 0,
  lastTranscriptMtimeMs: null,
  lastProcessedGenerationId: null,
  trialStartedAtMs: null,
};
