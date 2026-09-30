#!/usr/bin/env bun
import * as path from "node:path";
import * as process from "node:process";
import { evaluateRepository } from "./evals/routing";
import {
  describeBehavioralCase,
  describeSemanticCalibration,
  describeSemanticCalibrationMatrix,
  runBehavioralRepetitions,
  runSemanticCalibration,
  runSemanticCalibrationMatrix,
  type BehavioralResult,
  type SemanticCalibrationResult,
  type SemanticCalibrationMatrixResult,
} from "./evals/behavioral";

export function findRepoRoot(): string {
  return path.resolve(__dirname, "..");
}

function parseCliArgs(argv: string[]) {
  let root = findRepoRoot();
  let behavioral: string | null = null;
  let caseId: string | null = null;
  let repeat = 1;
  let dryRun = false;
  let model: string | null = null;
  let judge = false;
  let judgeModel: string | null = null;
  let calibrateJudge = false;
  let compareJudgeModel: string | null = null;
  let keepWorkspace = false;
  let timeout = 900;

  let i = 0;
  while (i < argv.length) {
    const arg = argv[i];
    if (arg === "--root") {
      root = path.resolve(argv[++i]);
    } else if (arg.startsWith("--root=")) {
      root = path.resolve(arg.slice("--root=".length));
    } else if (arg === "--behavioral") {
      behavioral = argv[++i];
    } else if (arg.startsWith("--behavioral=")) {
      behavioral = arg.slice("--behavioral=".length);
    } else if (arg === "--case") {
      caseId = argv[++i];
    } else if (arg.startsWith("--case=")) {
      caseId = arg.slice("--case=".length);
    } else if (arg === "--repeat") {
      repeat = parseInt(argv[++i], 10);
    } else if (arg.startsWith("--repeat=")) {
      repeat = parseInt(arg.slice("--repeat=".length), 10);
    } else if (arg === "--dry-run") {
      dryRun = true;
    } else if (arg === "--model") {
      model = argv[++i];
    } else if (arg.startsWith("--model=")) {
      model = arg.slice("--model=".length);
    } else if (arg === "--judge") {
      judge = true;
    } else if (arg === "--judge-model") {
      judgeModel = argv[++i];
    } else if (arg.startsWith("--judge-model=")) {
      judgeModel = arg.slice("--judge-model=".length);
    } else if (arg === "--calibrate-judge") {
      calibrateJudge = true;
    } else if (arg === "--compare-judge-model") {
      compareJudgeModel = argv[++i];
    } else if (arg.startsWith("--compare-judge-model=")) {
      compareJudgeModel = arg.slice("--compare-judge-model=".length);
    } else if (arg === "--keep-workspace") {
      keepWorkspace = true;
    } else if (arg === "--timeout") {
      timeout = parseInt(argv[++i], 10);
    } else if (arg.startsWith("--timeout=")) {
      timeout = parseInt(arg.slice("--timeout=".length), 10);
    } else {
      throw new Error(`unrecognized argument: ${arg}`);
    }
    i++;
  }

  return {
    root,
    behavioral,
    caseId,
    repeat,
    dryRun,
    model,
    judge,
    judgeModel,
    calibrateJudge,
    compareJudgeModel,
    keepWorkspace,
    timeout,
  };
}

function printBehavioralResult(
  result: BehavioralResult,
  options: { index: number; total: number; keepWorkspace: boolean }
) {
  const { index, total, keepWorkspace } = options;
  console.log(
    `Behavioral eval ${result.skill_name}/${result.case_id} run ${index}/${total}: ${
      result.mechanical_passed ? "MECHANICAL PASS" : "MECHANICAL FAIL"
    }`
  );
  console.log(`Changes: ${result.changes.length}`);
  if (result.unauthorized_mutations.length > 0) {
    console.log(`Unauthorized mutations: ${result.unauthorized_mutations.join(", ")}`);
  }
  if (result.missing_required_mutations.length > 0) {
    console.log(`Missing required mutations: ${result.missing_required_mutations.join(", ")}`);
  }
  const failedAssertions = result.file_assertions.filter((a) => !a.passed);
  if (failedAssertions.length > 0) {
    console.log(`Failed file assertions: ${failedAssertions.map((a) => a.path).join(", ")}`);
  }
  const failedTraceAssertions = result.trace_assertions.filter((a) => !a.passed);
  if (failedTraceAssertions.length > 0) {
    console.log(
      `Failed trace assertions: ${failedTraceAssertions
        .map((a) => `${a.assertion_type}: ${a.error}`)
        .join(", ")}`
    );
  }
  const judgment = result.semantic_judgment;
  if (judgment.status === "completed") {
    console.log(`Semantic judge: ${judgment.passed ? "PASS" : "FAIL"} (non-gating)`);
  } else if (judgment.status === "error") {
    console.log(`Semantic judge: ERROR (non-gating): ${judgment.error}`);
  }
  console.log(`Trace: ${result.trace_path}`);
  console.log(`Result: ${result.result_path}`);
  if (keepWorkspace) {
    console.log(`Workspace: ${result.workspace}`);
  }
}

function printSemanticCalibration(result: SemanticCalibrationResult) {
  const reps = result.repeat_count;
  console.log(
    `Semantic judge calibration ${result.skill_name}/${result.case_id}: ${
      result.passed ? "PASS" : "FAIL"
    } (${reps} repetition${reps !== 1 ? "s" : ""})`
  );
  for (const control of result.controls) {
    const status = control.matched ? "MATCH" : "MISMATCH";
    console.log(
      `Control ${JSON.stringify(control.control_id)} run ${control.repetition}/${
        result.repeat_count
      }: ${status}`
    );
    if (control.judgment.error) {
      console.log(`  Judge error: ${control.judgment.error}`);
    }
  }
  console.log(`Stability: ${result.stable ? "stable" : "variable"}`);
  if (result.usage === null) {
    console.log(`Usage: unavailable for all ${result.controls.length} judgments`);
  } else {
    console.log(
      `Usage (${result.usage_runs}/${result.controls.length} judgments): input=${result.usage.input_tokens}, cached=${result.usage.cached_input_tokens}, uncached=${result.usage.uncached_input_tokens}, output=${result.usage.output_tokens}, reasoning=${result.usage.reasoning_output_tokens}`
    );
  }
  console.log(`Summary: ${result.summary_path}`);
}

function printSemanticCalibrationMatrix(result: SemanticCalibrationMatrixResult) {
  console.log(
    `Cross-model judge calibration ${result.skill_name}/${result.case_id}: ${
      result.passed ? "PASS" : "FAIL"
    }`
  );
  for (const cal of result.calibrations) {
    console.log(
      `Model ${cal.judge_model}: ${cal.passed ? "PASS" : "FAIL"}, ${
        cal.stable ? "stable" : "variable"
      }`
    );
  }
  console.log(`Agreement: ${result.models_agree ? "complete" : "disagreement"}`);
  if (result.usage !== null) {
    console.log(
      `Usage (${result.usage_runs} judgments): input=${result.usage.input_tokens}, cached=${result.usage.cached_input_tokens}, uncached=${result.usage.uncached_input_tokens}, output=${result.usage.output_tokens}, reasoning=${result.usage.reasoning_output_tokens}`
    );
  }
  console.log(`Summary: ${result.summary_path}`);
}

export async function main(argv: string[] = process.argv.slice(2)): Promise<number> {
  let args: ReturnType<typeof parseCliArgs>;
  try {
    args = parseCliArgs(argv);
  } catch (err: any) {
    console.error(`ERROR: ${err.message}`);
    return 2;
  }

  if (args.behavioral) {
    if (!args.caseId) {
      console.error("ERROR: --case required with --behavioral");
      return 2;
    }
    const judgeModel = args.judgeModel || args.model;

    try {
      if (args.compareJudgeModel) {
        if (!judgeModel) {
          console.error("ERROR: --compare-judge-model requires a base judge model via --judge-model or --model");
          return 2;
        }
        const models = [judgeModel, args.compareJudgeModel];
        if (args.dryRun) {
          const plan = describeSemanticCalibrationMatrix(args.root, args.behavioral, args.caseId, {
            judge_models: models,
            repeat_count: args.repeat,
          });
          const sortedPlan = Object.fromEntries(
            Object.entries(plan).sort(([a], [b]) => a.localeCompare(b))
          );
          console.log(JSON.stringify(sortedPlan, null, 2));
          return 0;
        }
        const matrix = runSemanticCalibrationMatrix(args.root, args.behavioral, args.caseId, {
          judge_models: models,
          repeat_count: args.repeat,
          timeout_seconds: args.timeout,
        });
        printSemanticCalibrationMatrix(matrix);
        return matrix.passed ? 0 : 1;
      }

      if (args.calibrateJudge) {
        if (args.dryRun) {
          const plan = describeSemanticCalibration(args.root, args.behavioral, args.caseId, {
            judge_model: judgeModel,
            repeat_count: args.repeat,
          });
          const sortedPlan = Object.fromEntries(
            Object.entries(plan).sort(([a], [b]) => a.localeCompare(b))
          );
          console.log(JSON.stringify(sortedPlan, null, 2));
          return 0;
        }
        const calibration = runSemanticCalibration(args.root, args.behavioral, args.caseId, {
          judge_model: judgeModel,
          repeat_count: args.repeat,
          timeout_seconds: args.timeout,
        });
        printSemanticCalibration(calibration);
        return calibration.passed ? 0 : 1;
      }

      if (args.dryRun) {
        const plan = describeBehavioralCase(args.root, args.behavioral, args.caseId, {
          model: args.model,
          semantic_judge: args.judge,
          judge_model: args.judgeModel,
        });
        plan.repeat_count = args.repeat;
        const sortedPlan = Object.fromEntries(
          Object.entries(plan).sort(([a], [b]) => a.localeCompare(b))
        );
        console.log(JSON.stringify(sortedPlan, null, 2));
        return 0;
      }

      const batch = runBehavioralRepetitions(args.root, args.behavioral, args.caseId, {
        repeat_count: args.repeat,
        model: args.model,
        semantic_judge: args.judge,
        judge_model: args.judgeModel,
        timeout_seconds: args.timeout,
        keep_workspace: args.keepWorkspace,
      });

      for (let index = 0; index < batch.runs.length; index++) {
        printBehavioralResult(batch.runs[index], {
          index: index + 1,
          total: batch.runs.length,
          keepWorkspace: args.keepWorkspace,
        });
      }

      console.log(`Summary: ${batch.summary_path}`);
      console.log(
        `Stability: mechanical=${batch.mechanically_stable ? "stable" : "variable"}, mutations=${
          batch.mutations_stable ? "stable" : "variable"
        }, environment=${batch.execution_environments_stable ? "stable" : "variable"}`
      );
      if (batch.usage === null) {
        console.log(`Usage: unavailable for all ${batch.runs.length} runs`);
      } else {
        console.log(
          `Usage (${batch.usage_runs}/${batch.runs.length} runs): input=${batch.usage.input_tokens}, cached=${batch.usage.cached_input_tokens}, uncached=${batch.usage.uncached_input_tokens}, output=${batch.usage.output_tokens}, reasoning=${batch.usage.reasoning_output_tokens}`
        );
      }

      if (args.judge) {
        console.log("Semantic judge: NON-GATING; see per-run results");
      } else {
        console.log("Semantic expectations: UNGRADED");
      }

      return batch.mechanical_passes === batch.runs.length ? 0 : 1;
    } catch (err: any) {
      console.error(`ERROR: ${err.message}`);
      return 2;
    }
  }

  if (
    args.caseId ||
    args.dryRun ||
    args.model ||
    args.judge ||
    args.judgeModel ||
    args.calibrateJudge ||
    args.compareJudgeModel ||
    args.keepWorkspace ||
    args.repeat !== 1
  ) {
    console.error("ERROR: behavioral options require --behavioral");
    return 2;
  }

  const report = evaluateRepository(args.root);

  console.log(
    `Evaluated ${report.skillCount} skills across ${report.caseFiles} routing case files.`
  );
  for (const warning of report.warnings) {
    console.log(`WARN: ${warning}`);
  }
  for (const error of report.errors) {
    console.log(`ERROR: ${error}`);
  }

  const rate =
    report.rankOneRate === null
      ? "n/a"
      : `${Math.round(report.rankOneRate * 100)}%`;

  console.log(
    `Routing checks: ${report.routingPassed}/${report.routingChecks} passed; positive rank-one rate: ${rate}.`
  );

  return report.errors.length > 0 ? 1 : 0;
}

if (import.meta.main) {
  main().then((code) => {
    if (code !== 0) {
      process.exit(code);
    }
  });
}
