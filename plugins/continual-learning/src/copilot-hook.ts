import { resolve } from "node:path";
import { evaluateCadence } from "./cadence.ts";
import {
  loadCadenceConfigFromEnv,
  loadState,
  saveState,
  type HookExecutionOptions,
} from "./state.ts";
import {
  runContinualLearningLoop,
  type ContinualLearningRunnerOptions,
} from "./runner.ts";
import type {
  CopilotSessionEndInput,
  CopilotSessionEndOutput,
} from "./types/copilot.ts";

export interface CopilotHookExecutionOptions
  extends HookExecutionOptions,
    ContinualLearningRunnerOptions {}

/**
 * Handles Copilot CLI sessionEnd lifecycle hook according to Rule 5.
 */
export function handleCopilotSessionEndHook(
  input: CopilotSessionEndInput,
  options?: CopilotHookExecutionOptions
): CopilotSessionEndOutput {
  const now = options?.now ?? Date.now();
  const config = options?.config ?? loadCadenceConfigFromEnv();

  const workspacePath =
    input.workspacePath ?? input.workspace_path ?? process.cwd();

  const statePath =
    options?.statePath ??
    process.env.CONTINUAL_LEARNING_STATE_PATH ??
    resolve(workspacePath, ".copilot/state/continual-learning.json");

  const state = loadState(statePath);

  // Check turn counting
  const countedTurn = input.status !== "error";
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
    const transcriptPath =
      options?.transcriptPath ??
      input.transcriptPath ??
      input.transcript_path ??
      null;

    const runnerResult = runContinualLearningLoop(workspacePath, state, {
      indexPath: options?.indexPath,
      agentsPath: options?.agentsPath,
      statePath,
      transcriptPath,
      candidatePaths: options?.candidatePaths,
      transcriptsDir: options?.transcriptsDir,
      now,
      extractor: options?.extractor,
      updates: options?.updates,
    });

    state.lastRunAtMs = now;
    state.turnsSinceLastRun = 0;
    saveState(statePath, state);

    return {
      status: "ok",
      message: runnerResult.message ?? "Cadence met, continual learning executed.",
    };
  }

  state.turnsSinceLastRun = turnsSinceLastRun;
  saveState(statePath, state);

  return {
    status: "skipped",
    message: "Cadence not met.",
  };
}

async function readStdin(): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(typeof chunk === "string" ? Buffer.from(chunk) : chunk);
  }
  return Buffer.concat(chunks).toString("utf-8");
}

async function main(): Promise<void> {
  let input: CopilotSessionEndInput = {};
  try {
    const raw = await readStdin();
    if (raw.trim().length > 0) {
      input = JSON.parse(raw) as CopilotSessionEndInput;
    }
  } catch {
    input = {};
  }

  try {
    const output = handleCopilotSessionEndHook(input);
    process.stdout.write(`${JSON.stringify(output)}\n`);
    process.exit(0);
  } catch (err) {
    console.error("[copilot-hook] Error:", err);
    process.stdout.write(
      `${JSON.stringify({ status: "error", message: String(err) })}\n`
    );
    process.exit(0);
  }
}

if (process.argv[1] && process.argv[1].endsWith("copilot-hook.ts")) {
  void main();
}
