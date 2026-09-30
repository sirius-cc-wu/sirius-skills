import { describe, expect, test, beforeEach, afterEach } from "bun:test";
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import {
  buildCodexCommand,
  describeBehavioralCase,
  runBehavioralCase,
  runBehavioralRepetitions,
  describeSemanticCalibration,
  runSemanticCalibration,
  describeSemanticCalibrationMatrix,
  runSemanticCalibrationMatrix,
} from "../scripts/evals/behavioral";

function makeTempDir(): string {
  return fs.mkdtempSync(path.join(os.tmpdir(), "sirius-test-behavioral-"));
}

function writeSkill(root: string, name: string, description: string): void {
  const skillFile = path.join(root, "skills", name, "SKILL.md");
  fs.mkdirSync(path.dirname(skillFile), { recursive: true });
  fs.writeFileSync(
    skillFile,
    `---\nname: ${name}\ndescription: ${description}\n---\n\n# ${name}\n`,
    "utf-8"
  );
}

function writeCase(root: string, name: string, data: Record<string, any>): void {
  const caseFile = path.join(root, "evals", "cases", `${name}.json`);
  fs.mkdirSync(path.dirname(caseFile), { recursive: true });
  fs.writeFileSync(caseFile, JSON.stringify(data, null, 2), "utf-8");
}

function writeBehaviorFixture(
  root: string,
  options: {
    allowed_mutations: string[];
    required_mutations?: string[];
    semantic_rubric?: Array<Record<string, any>>;
    semantic_controls?: Array<Record<string, any>>;
    workspace_mode?: string;
    trace_assertions?: Array<Record<string, any>>;
  }
): void {
  writeSkill(root, "implementation", "Implement behavior with executable tests.");
  const fixture = path.join(root, "evals", "fixtures", "example");
  fs.mkdirSync(path.join(fixture, "src"), { recursive: true });
  fs.mkdirSync(path.join(fixture, "tests"), { recursive: true });

  const mode = options.workspace_mode ?? "mutable";
  const fixtureValue = mode === "read-only" ? "fixed\n" : "broken\n";
  fs.writeFileSync(path.join(fixture, "src", "value.txt"), fixtureValue, "utf-8");

  const verifierScript = path.join(fixture, "tests", "verify.sh");
  fs.writeFileSync(
    verifierScript,
    `#!/usr/bin/env bash\nset -euo pipefail\nval=$(cat src/value.txt)\n[ "$val" = "fixed" ]\n`,
    "utf-8"
  );
  fs.chmodSync(verifierScript, 0o755);

  const behavioralCase: Record<string, any> = {
    id: "fix-value",
    prompt: mode === "read-only" ? "Inspect the value without changing it." : "Fix the value.",
    expected_output: mode === "read-only" ? "The verified value remains unchanged." : "The verifier passes.",
    expectations: [
      mode === "read-only" ? "The verified value is not changed." : "The broken value is corrected.",
    ],
    prohibitions: ["Do not change unrelated files."],
    fixture: "example",
    workspace_mode: mode,
    allowed_mutations: options.allowed_mutations,
    required_mutations: options.required_mutations ?? ["src/**"],
    checks: [["bash", "tests/verify.sh"]],
  };

  if (options.trace_assertions) {
    behavioralCase.trace_assertions = options.trace_assertions;
  }
  if (options.semantic_rubric) {
    behavioralCase.semantic_rubric = options.semantic_rubric;
  }
  if (options.semantic_controls) {
    behavioralCase.semantic_controls = options.semantic_controls;
  }

  writeCase(root, "implementation", {
    skill_name: "implementation",
    trigger: { positive: [], negative: [] },
    evals: [behavioralCase],
  });
}

function writeFakeExecutor(tmpDir: string, mutationRelPath: string): string[] {
  const scriptPath = path.join(tmpDir, "fake_executor.sh");
  fs.writeFileSync(
    scriptPath,
    `#!/usr/bin/env bash\n` +
      `mkdir -p $(dirname "${mutationRelPath}")\n` +
      `printf "fixed\\n" > "${mutationRelPath}"\n` +
      `echo '{"type": "turn.completed", "usage": {"input_tokens": 1}}'\n`,
    "utf-8"
  );
  fs.chmodSync(scriptPath, 0o755);
  return ["bash", scriptPath];
}

function writeNoopExecutor(tmpDir: string): string[] {
  const scriptPath = path.join(tmpDir, "noop_executor.sh");
  fs.writeFileSync(
    scriptPath,
    `#!/usr/bin/env bash\n` +
      `echo '{"type": "turn.completed"}'\n`,
    "utf-8"
  );
  fs.chmodSync(scriptPath, 0o755);
  return ["bash", scriptPath];
}

describe("behavioral evaluation", () => {
  let tmpDir: string;

  beforeEach(() => {
    tmpDir = makeTempDir();
  });

  afterEach(() => {
    if (fs.existsSync(tmpDir)) {
      try {
        fs.rmSync(tmpDir, { recursive: true, force: true });
      } catch {}
    }
  });

  test("buildCodexCommand sets proper defaults and flags", () => {
    const cmd1 = buildCodexCommand("/tmp/ws");
    expect(cmd1).toEqual([
      "codex",
      "exec",
      "--ephemeral",
      "--json",
      "--sandbox",
      "workspace-write",
      "--ignore-user-config",
      "--cd",
      "/tmp/ws",
      "-",
    ]);

    const cmd2 = buildCodexCommand("/tmp/ws", {
      model: "gpt-5.6-sol",
      sandbox: "read-only",
    });
    expect(cmd2).toEqual([
      "codex",
      "exec",
      "--ephemeral",
      "--json",
      "--sandbox",
      "read-only",
      "--ignore-user-config",
      "--cd",
      "/tmp/ws",
      "--model",
      "gpt-5.6-sol",
      "-",
    ]);
  });

  test("describeBehavioralCase reports complete execution plan", () => {
    writeBehaviorFixture(tmpDir, { allowed_mutations: ["src/**"] });
    const plan = describeBehavioralCase(tmpDir, "implementation", "fix-value");

    expect(plan.skill_name).toBe("implementation");
    expect(plan.case_id).toBe("fix-value");
    expect(plan.fixture).toBe("evals/fixtures/example");
    expect(plan.workspace_mode).toBe("mutable");
    expect(plan.allowed_mutations).toEqual(["src/**"]);
  });

  test("runBehavioralCase executes check and records mutations", () => {
    writeBehaviorFixture(tmpDir, { allowed_mutations: ["src/**"] });
    const executor = writeFakeExecutor(tmpDir, "src/value.txt");

    const result = runBehavioralCase(tmpDir, "implementation", "fix-value", {
      executor_command: executor,
    });

    expect(result.mechanical_passed).toBe(true);
    expect(result.executor_returncode).toBe(0);
    expect(result.unauthorized_mutations).toEqual([]);
    expect(result.missing_required_mutations).toEqual([]);
    expect(result.changes.length).toBe(1);
    expect(result.changes[0].path).toBe("src/value.txt");
    expect(result.changes[0].kind).toBe("modified");
  });

  test("runBehavioralCase fails on unauthorized mutation", () => {
    writeBehaviorFixture(tmpDir, { allowed_mutations: ["src/**"] });
    const executor = writeFakeExecutor(tmpDir, "unauthorized.txt");

    const result = runBehavioralCase(tmpDir, "implementation", "fix-value", {
      executor_command: executor,
    });

    expect(result.mechanical_passed).toBe(false);
    expect(result.unauthorized_mutations).toEqual(["unauthorized.txt"]);
  });

  test("runBehavioralCase fails on missing required mutation", () => {
    writeBehaviorFixture(tmpDir, {
      allowed_mutations: ["src/**"],
      required_mutations: ["src/required.txt"],
    });
    const executor = writeFakeExecutor(tmpDir, "src/value.txt");

    const result = runBehavioralCase(tmpDir, "implementation", "fix-value", {
      executor_command: executor,
    });

    expect(result.mechanical_passed).toBe(false);
    expect(result.missing_required_mutations).toEqual(["src/required.txt"]);
  });

  test("runBehavioralCase fails when check fails", () => {
    writeBehaviorFixture(tmpDir, { allowed_mutations: ["src/**"] });
    const executor = writeNoopExecutor(tmpDir); // Does not fix value.txt, so verify.sh fails

    const result = runBehavioralCase(tmpDir, "implementation", "fix-value", {
      executor_command: executor,
    });

    expect(result.mechanical_passed).toBe(false);
    expect(result.checks[0].returncode).not.toBe(0);
  });

  test("runBehavioralRepetitions runs multiple iterations and creates summary", () => {
    writeBehaviorFixture(tmpDir, { allowed_mutations: ["src/**"] });
    const executor = writeFakeExecutor(tmpDir, "src/value.txt");

    const batch = runBehavioralRepetitions(tmpDir, "implementation", "fix-value", {
      repeat_count: 2,
      executor_command: executor,
    });

    expect(batch.runs.length).toBe(2);
    expect(batch.mechanical_passes).toBe(2);
    expect(batch.mechanically_stable).toBe(true);
    expect(fs.existsSync(batch.summary_path)).toBe(true);
  });

  test("runBehavioralCase verifies file assertions including plantuml scope", () => {
    writeBehaviorFixture(tmpDir, { allowed_mutations: ["src/**"] });
    const fixtureCase = JSON.parse(
      fs.readFileSync(path.join(tmpDir, "evals", "cases", "implementation.json"), "utf-8")
    );
    fixtureCase.evals[0].file_assertions = [
      {
        path: "src/diagram.md",
        scope: "plantuml",
        contains: ["Order --> Payment"],
        not_contains: ["Order --> Invalid"],
      },
    ];
    fs.writeFileSync(
      path.join(tmpDir, "evals", "cases", "implementation.json"),
      JSON.stringify(fixtureCase),
      "utf-8"
    );

    const scriptPath = path.join(tmpDir, "diagram_executor.sh");
    fs.writeFileSync(
      scriptPath,
      `#!/usr/bin/env bash\n` +
        `printf "fixed\\n" > src/value.txt\n` +
        `cat <<'EOF' > src/diagram.md\n` +
        `Here is the diagram:\n` +
        `\`\`\`plantuml\n` +
        `Order --> Payment\n` +
        `\`\`\`\n` +
        `EOF\n` +
        `echo '{"type": "turn.completed"}'\n`,
      "utf-8"
    );
    fs.chmodSync(scriptPath, 0o755);

    const result = runBehavioralCase(tmpDir, "implementation", "fix-value", {
      executor_command: ["bash", scriptPath],
    });

    expect(result.mechanical_passed).toBe(true);
    expect(result.file_assertions.length).toBe(1);
    expect(result.file_assertions[0].passed).toBe(true);
  });

  test("describeSemanticCalibration and runSemanticCalibration execute with mock judge", () => {
    const rubric = [
      { id: "c1", criterion: "Validates requirements." },
    ];
    const controls = [
      {
        id: "ctrl-pos",
        response: "I validate requirements carefully.",
        expected_criteria: [{ id: "c1", passed: true }],
      },
      {
        id: "ctrl-neg",
        response: "I skip all requirements.",
        expected_criteria: [{ id: "c1", passed: false }],
      },
    ];

    writeBehaviorFixture(tmpDir, {
      allowed_mutations: ["src/**"],
      semantic_rubric: rubric,
      semantic_controls: controls,
    });

    const plan = describeSemanticCalibration(tmpDir, "implementation", "fix-value");
    expect(plan.skill_name).toBe("implementation");
    expect(plan.controls.length).toBe(2);

    const judgeScript = path.join(tmpDir, "mock_judge.sh");
    // If prompt contains "skip all requirements", passed is false; else true
    fs.writeFileSync(
      judgeScript,
      `#!/usr/bin/env bash\n` +
        `input=$(cat)\n` +
        `passed="true"\n` +
        `if echo "$input" | grep -q "skip all requirements"; then\n` +
        `  passed="false"\n` +
        `fi\n` +
        `echo '{"type": "item.completed", "item": {"type": "agent_message", "text": "{\\"criteria\\": [{\\"id\\": \\"c1\\", \\"passed\\": '"$passed"', \\"reason\\": \\"ok\\"}]}"}}'\n`,
      "utf-8"
    );
    fs.chmodSync(judgeScript, 0o755);

    const calResult = runSemanticCalibration(tmpDir, "implementation", "fix-value", {
      judge_model: "test-model",
      judge_executor_command: ["bash", judgeScript],
    });

    expect(calResult.passed).toBe(true);
    expect(calResult.controls.length).toBe(2);
    expect(calResult.controls[0].matched).toBe(true);
    expect(calResult.controls[1].matched).toBe(true);
  });

  test("describeSemanticCalibrationMatrix and runSemanticCalibrationMatrix check cross-model agreement", () => {
    const rubric = [{ id: "c1", criterion: "Checks error." }];
    const controls = [
      {
        id: "pos",
        response: "error checked",
        expected_criteria: [{ id: "c1", passed: true }],
      },
      {
        id: "neg",
        response: "no error check",
        expected_criteria: [{ id: "c1", passed: false }],
      },
    ];

    writeBehaviorFixture(tmpDir, {
      allowed_mutations: ["src/**"],
      semantic_rubric: rubric,
      semantic_controls: controls,
    });

    const plan = describeSemanticCalibrationMatrix(tmpDir, "implementation", "fix-value", {
      judge_models: ["model-a", "model-b"],
    });
    expect(plan.judge_models).toEqual(["model-a", "model-b"]);

    const judgeScript = path.join(tmpDir, "mock_matrix_judge.sh");
    fs.writeFileSync(
      judgeScript,
      `#!/usr/bin/env bash\n` +
        `input=$(cat)\n` +
        `passed="true"\n` +
        `if echo "$input" | grep -q "no error check"; then\n` +
        `  passed="false"\n` +
        `fi\n` +
        `echo '{"type": "item.completed", "item": {"type": "agent_message", "text": "{\\"criteria\\": [{\\"id\\": \\"c1\\", \\"passed\\": '"$passed"', \\"reason\\": \\"ok\\"}]}"}}'\n`,
      "utf-8"
    );
    fs.chmodSync(judgeScript, 0o755);

    const matrixResult = runSemanticCalibrationMatrix(tmpDir, "implementation", "fix-value", {
      judge_models: ["model-a", "model-b"],
      judge_executor_commands: {
        "model-a": ["bash", judgeScript],
        "model-b": ["bash", judgeScript],
      },
    });

    expect(matrixResult.passed).toBe(true);
    expect(matrixResult.models_agree).toBe(true);
    expect(matrixResult.calibrations.length).toBe(2);
  });
});
