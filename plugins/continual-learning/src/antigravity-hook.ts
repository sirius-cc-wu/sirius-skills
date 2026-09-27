import { resolve } from "node:path";
import { evaluateCadence } from "./cadence.ts";
import {
  DEFAULT_CADENCE_CONFIG,
  INITIAL_STATE,
  type CadenceConfig,
  type ContinuousLearningState,
} from "./types/common.ts";
import type {
  AntigravityStopHookInput,
  AntigravityStopHookOutput,
} from "./types/antigravity.ts";
import {
  loadCadenceConfigFromEnv,
  loadState,
  saveState,
  type HookExecutionOptions,
} from "./state.ts";

export {
  loadCadenceConfigFromEnv,
  loadState,
  saveState,
  type HookExecutionOptions,
};

/**
 * Handles Antigravity CLI Stop hook event according to Rule 4.
 */
export function handleAntigravityStopHook(
  input: AntigravityStopHookInput,
  options?: HookExecutionOptions
): AntigravityStopHookOutput {
  const now = options?.now ?? Date.now();
  const config = options?.config ?? loadCadenceConfigFromEnv();

  const statePath =
    options?.statePath ??
    process.env.CONTINUAL_LEARNING_STATE_PATH ??
    (input.workspacePaths && input.workspacePaths.length > 0
      ? resolve(input.workspacePaths[0], ".gemini/state/continual-learning.json")
      : resolve(".gemini/state/continual-learning.json"));

  const state = loadState(statePath);

  // Avoid double-processing the same generation
  if (input.generationId) {
    if (input.generationId === state.lastProcessedGenerationId) {
      return { decision: "allow" };
    }
    state.lastProcessedGenerationId = input.generationId;
  }

  // Check turn counting
  const countedTurn =
    input.status !== "error" &&
    (input.loopCount === 0 || input.loopCount === undefined);
  const turnIncrement = countedTurn ? 1 : 0;
  const turnsSinceLastRun = state.turnsSinceLastRun + turnIncrement;

  if (config.trialMode && countedTurn && state.trialStartedAtMs === null) {
    state.trialStartedAtMs = now;
  }

  const cadence = evaluateCadence(
    { ...state, turnsSinceLastRun },
    config,
    now
  );

  if (cadence.shouldRun) {
    state.lastRunAtMs = now;
    state.turnsSinceLastRun = 0;
    saveState(statePath, state);

    return {
      decision: "continue",
      reason:
        "Trigger continual-learning skill to update AGENTS.md from recent transcripts.",
    };
  }

  state.turnsSinceLastRun = turnsSinceLastRun;
  saveState(statePath, state);

  return { decision: "allow" };
}

async function readStdin(): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(typeof chunk === "string" ? Buffer.from(chunk) : chunk);
  }
  return Buffer.concat(chunks).toString("utf-8");
}

async function main(): Promise<void> {
  let input: AntigravityStopHookInput = {};
  try {
    const raw = await readStdin();
    if (raw.trim().length > 0) {
      input = JSON.parse(raw) as AntigravityStopHookInput;
    }
  } catch {
    // If stdin parsing fails, fall back to empty input
    input = {};
  }

  try {
    const output = handleAntigravityStopHook(input);
    process.stdout.write(`${JSON.stringify(output)}\n`);
  } catch (err) {
    console.error("[antigravity-hook] Error:", err);
    process.stdout.write(`${JSON.stringify({ decision: "allow" })}\n`);
  }
}

if (process.argv[1] && process.argv[1].endsWith("antigravity-hook.ts")) {
  void main();
}
