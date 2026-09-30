import * as fs from "node:fs";
import * as path from "node:path";
import {
  tokenize,
  countTerms,
  tfidfVector,
  cosineSimilarity,
  rankSkills,
  type TermFrequency,
} from "./nlp";

export const COLLISION_WARNING = 0.6;
export const COLLISION_ERROR = 0.9;
export const MIN_POSITIVE = 3;
export const MIN_NEGATIVE = 2;
export const MIN_BEHAVIORAL = 1;

export class EvaluationReport {
  skillCount = 0;
  caseFiles = 0;
  routingChecks = 0;
  routingPassed = 0;
  positiveChecks = 0;
  rankOnePositives = 0;
  errors: string[] = [];
  warnings: string[] = [];

  get rankOneRate(): number | null {
    if (!this.positiveChecks) {
      return null;
    }
    return this.rankOnePositives / this.positiveChecks;
  }
}

export function frontmatterValue(source: string, key: string): string | null {
  const pattern = new RegExp(`^${key}:\\s*(.+)$`, "m");
  const match = source.match(pattern);
  if (!match) {
    return null;
  }
  let value = match[1].trim();
  if (
    value.length >= 2 &&
    value[0] === value[value.length - 1] &&
    (value[0] === '"' || value[0] === "'")
  ) {
    return value.slice(1, -1);
  }
  return value;
}

export function loadSkillDescriptions(root: string): Record<string, string> {
  const descriptions: Record<string, string> = {};
  const skillsDir = path.join(root, "skills");
  if (!fs.existsSync(skillsDir)) {
    return descriptions;
  }

  const entries = fs.readdirSync(skillsDir, { withFileTypes: true });
  const sortedDirs = entries
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();

  for (const name of sortedDirs) {
    const skillPath = path.join(skillsDir, name, "SKILL.md");
    if (fs.existsSync(skillPath)) {
      const source = fs.readFileSync(skillPath, "utf-8");
      const skillName = frontmatterValue(source, "name");
      const desc = frontmatterValue(source, "description");
      if (skillName && desc) {
        descriptions[skillName] = desc;
      }
    }
  }

  return descriptions;
}

function isValidStringList(value: unknown, options: { allowEmpty?: boolean } = {}): boolean {
  const allowEmpty = options.allowEmpty ?? true;
  if (!Array.isArray(value)) {
    return false;
  }
  if (!allowEmpty && value.length === 0) {
    return false;
  }
  return value.every(
    (item) => typeof item === "string" && item.trim().length > 0
  );
}

export function validateBehavioralCases(
  filename: string,
  cases: unknown,
  report: EvaluationReport
): void {
  if (!Array.isArray(cases)) {
    report.errors.push(`${filename}: 'evals' must be a list`);
    return;
  }

  const seenIds = new Set<string | number>();
  for (const caseItem of cases) {
    if (typeof caseItem !== "object" || caseItem === null || Array.isArray(caseItem)) {
      report.errors.push(`${filename}: each behavioral eval must be an object`);
      continue;
    }
    const c = caseItem as Record<string, any>;
    const caseId = c.id;
    const validId =
      (typeof caseId === "string" && caseId.trim().length > 0) ||
      (typeof caseId === "number" && !isNaN(caseId));

    if (!validId) {
      report.errors.push(`${filename}: behavioral eval has an invalid id`);
    } else if (seenIds.has(caseId)) {
      report.errors.push(`${filename}: duplicate behavioral eval id ${JSON.stringify(caseId)}`);
    } else {
      seenIds.add(caseId);
    }

    for (const key of ["prompt", "expected_output"]) {
      const val = c[key];
      if (typeof val !== "string" || !val.trim()) {
        report.errors.push(
          `${filename}: behavioral eval ${JSON.stringify(caseId)} needs non-empty '${key}'`
        );
      }
    }

    if (!isValidStringList(c.expectations, { allowEmpty: false })) {
      report.errors.push(
        `${filename}: behavioral eval ${JSON.stringify(caseId)} needs expectations`
      );
    }

    for (const key of ["prohibitions", "allowed_mutations"]) {
      if (key in c && !isValidStringList(c[key])) {
        report.errors.push(
          `${filename}: behavioral eval ${JSON.stringify(caseId)} has invalid '${key}'`
        );
      }
    }

    if ("required_mutations" in c && !isValidStringList(c.required_mutations)) {
      report.errors.push(
        `${filename}: behavioral eval ${JSON.stringify(caseId)} has invalid 'required_mutations'`
      );
    }

    const fixture = c.fixture;
    const workspaceMode = c.workspace_mode ?? "mutable";
    if (workspaceMode !== "mutable" && workspaceMode !== "read-only") {
      report.errors.push(
        `${filename}: behavioral eval ${JSON.stringify(caseId)} has invalid 'workspace_mode'`
      );
    }

    if (fixture !== undefined) {
      if (typeof fixture !== "string" || !fixture.trim()) {
        report.errors.push(
          `${filename}: behavioral eval ${JSON.stringify(caseId)} has invalid 'fixture'`
        );
      } else {
        const allowedMutations = c.allowed_mutations;
        if (!isValidStringList(allowedMutations)) {
          report.errors.push(
            `${filename}: fixture-backed eval ${JSON.stringify(caseId)} needs allowed_mutations`
          );
        } else if (workspaceMode === "mutable" && allowedMutations.length === 0) {
          report.errors.push(
            `${filename}: mutable eval ${JSON.stringify(caseId)} needs allowed mutations`
          );
        } else if (workspaceMode === "read-only" && allowedMutations.length > 0) {
          report.errors.push(
            `${filename}: read-only eval ${JSON.stringify(caseId)} must not allow mutations`
          );
        }

        if (
          workspaceMode === "read-only" &&
          Array.isArray(c.required_mutations) &&
          c.required_mutations.length !== 0
        ) {
          report.errors.push(
            `${filename}: read-only eval ${JSON.stringify(caseId)} must declare empty required_mutations`
          );
        }
      }
    }

    const checks = c.checks ?? [];
    if (
      !Array.isArray(checks) ||
      checks.some(
        (cmd) =>
          !Array.isArray(cmd) ||
          cmd.length === 0 ||
          cmd.some((arg) => typeof arg !== "string" || !arg)
      )
    ) {
      report.errors.push(
        `${filename}: behavioral eval ${JSON.stringify(caseId)} has invalid 'checks'`
      );
    }

    const fileAssertions = c.file_assertions ?? [];
    if (
      !Array.isArray(fileAssertions) ||
      fileAssertions.some(
        (assertion) =>
          typeof assertion !== "object" ||
          assertion === null ||
          typeof assertion.path !== "string" ||
          !assertion.path ||
          !["file", "plantuml"].includes(assertion.scope ?? "file") ||
          !isValidStringList(assertion.contains ?? []) ||
          !isValidStringList(assertion.not_contains ?? [])
      )
    ) {
      report.errors.push(
        `${filename}: behavioral eval ${JSON.stringify(caseId)} has invalid 'file_assertions'`
      );
    }

    const traceAssertions = c.trace_assertions ?? [];
    if (
      !Array.isArray(traceAssertions) ||
      traceAssertions.some(
        (assertion) =>
          typeof assertion !== "object" ||
          assertion === null ||
          assertion.type !== "red_green" ||
          !isValidStringList(assertion.command_contains, { allowEmpty: false }) ||
          !isValidStringList(assertion.mutation_patterns, { allowEmpty: false })
      )
    ) {
      report.errors.push(
        `${filename}: behavioral eval ${JSON.stringify(caseId)} has invalid 'trace_assertions'`
      );
    }

    const semanticRubric = c.semantic_rubric ?? [];
    const rubricIds = new Set<string | number>();
    const orderedRubricIds: Array<string | number> = [];
    if (!Array.isArray(semanticRubric)) {
      report.errors.push(
        `${filename}: behavioral eval ${JSON.stringify(caseId)} has invalid 'semantic_rubric'`
      );
    } else {
      for (const criterion of semanticRubric) {
        const criterionId = typeof criterion === "object" && criterion !== null ? criterion.id : null;
        const description =
          typeof criterion === "object" && criterion !== null ? criterion.criterion : null;
        const validCriterionId =
          (typeof criterionId === "string" && criterionId.trim().length > 0) ||
          (typeof criterionId === "number" && !isNaN(criterionId));

        if (
          !validCriterionId ||
          typeof description !== "string" ||
          !description.trim()
        ) {
          report.errors.push(
            `${filename}: behavioral eval ${JSON.stringify(caseId)} has invalid semantic rubric criterion`
          );
          continue;
        }

        if (rubricIds.has(criterionId)) {
          report.errors.push(
            `${filename}: behavioral eval ${JSON.stringify(caseId)} has duplicate semantic rubric id ${JSON.stringify(criterionId)}`
          );
        }
        rubricIds.add(criterionId);
        orderedRubricIds.push(criterionId);
      }
    }

    const semanticControls = c.semantic_controls ?? [];
    if (!Array.isArray(semanticControls)) {
      report.errors.push(
        `${filename}: behavioral eval ${JSON.stringify(caseId)} has invalid 'semantic_controls'`
      );
    } else {
      const controlIds = new Set<string | number>();
      const polarities = new Map<string | number, Set<boolean>>();
      for (const id of orderedRubricIds) {
        polarities.set(id, new Set<boolean>());
      }
      let controlsValid = true;

      if (semanticControls.length > 0 && orderedRubricIds.length === 0) {
        controlsValid = false;
        report.errors.push(
          `${filename}: behavioral eval ${JSON.stringify(caseId)} has semantic controls without a semantic rubric`
        );
      }

      for (const control of semanticControls) {
        const controlId = typeof control === "object" && control !== null ? control.id : null;
        const response = typeof control === "object" && control !== null ? control.response : null;
        const expected = typeof control === "object" && control !== null ? control.expected_criteria : null;

        const validControlId =
          (typeof controlId === "string" && controlId.trim().length > 0) ||
          (typeof controlId === "number" && !isNaN(controlId));

        if (
          !validControlId ||
          controlIds.has(controlId) ||
          typeof response !== "string" ||
          !response.trim() ||
          !Array.isArray(expected)
        ) {
          controlsValid = false;
          report.errors.push(
            `${filename}: behavioral eval ${JSON.stringify(caseId)} has invalid semantic control`
          );
          continue;
        }
        controlIds.add(controlId);

        const expectedIds: Array<string | number> = [];
        let validExpectations = true;

        for (const crit of expected) {
          const expectedId = typeof crit === "object" && crit !== null ? crit.id : null;
          const passed = typeof crit === "object" && crit !== null ? crit.passed : null;

          if (
            !rubricIds.has(expectedId) ||
            expectedIds.includes(expectedId) ||
            typeof passed !== "boolean"
          ) {
            validExpectations = false;
            break;
          }
          expectedIds.push(expectedId);
        }

        if (!validExpectations) {
          controlsValid = false;
          report.errors.push(
            `${filename}: semantic control ${JSON.stringify(controlId)} has invalid expectations`
          );
        } else if (
          expectedIds.length !== orderedRubricIds.length ||
          expectedIds.some((val, idx) => val !== orderedRubricIds[idx])
        ) {
          controlsValid = false;
          report.errors.push(
            `${filename}: semantic control ${JSON.stringify(controlId)} must cover semantic rubric ids in rubric order`
          );
        } else {
          for (const crit of expected) {
            polarities.get(crit.id)!.add(crit.passed);
          }
        }
      }

      const missingPolarities: Array<string | number> = [];
      for (const [criterionId, values] of polarities.entries()) {
        if (values.size !== 2 || !values.has(true) || !values.has(false)) {
          missingPolarities.push(criterionId);
        }
      }

      if (semanticControls.length > 0 && controlsValid && missingPolarities.length > 0) {
        report.errors.push(
          `${filename}: semantic controls must exercise true and false for rubric ids ${JSON.stringify(missingPolarities)}`
        );
      }
    }

    const trustLevel = c.trust_level;
    if (trustLevel !== undefined && trustLevel !== null && trustLevel !== "provisional" && trustLevel !== "fixture-backed") {
      report.errors.push(
        `${filename}: behavioral eval ${JSON.stringify(caseId)} has invalid 'trust_level'`
      );
    }
  }
}

export function checkCollisions(
  descriptions: Record<string, string>,
  report: EvaluationReport
): void {
  const names = Object.keys(descriptions).sort();
  const terms = new Map<string, TermFrequency>();
  for (const name of names) {
    terms.set(name, countTerms(tokenize(descriptions[name])));
  }
  const documents = Array.from(terms.values());
  const vectors = new Map<string, Map<string, number>>();
  for (const name of names) {
    vectors.set(name, tfidfVector(terms.get(name)!, documents));
  }

  for (let i = 0; i < names.length; i++) {
    const left = names[i];
    for (let j = i + 1; j < names.length; j++) {
      const right = names[j];
      const similarity = cosineSimilarity(vectors.get(left)!, vectors.get(right)!);
      const percent = Math.round(similarity * 100);
      const message = `description collision: ${left} and ${right} are ${percent}% similar`;
      if (similarity >= COLLISION_ERROR) {
        report.errors.push(message);
      } else if (similarity >= COLLISION_WARNING) {
        report.warnings.push(message.replace("collision", "overlap"));
      }
    }
  }
}

export function checkPositive(
  filename: string,
  expected: string,
  trigger: unknown,
  descriptions: Record<string, string>,
  report: EvaluationReport
): void {
  report.routingChecks++;
  report.positiveChecks++;

  if (typeof trigger !== "object" || trigger === null || Array.isArray(trigger)) {
    report.errors.push(`${filename}: positive trigger must be an object`);
    return;
  }
  const t = trigger as Record<string, any>;
  const prompt = t.prompt;
  const topK = t.top_k ?? 3;

  if (typeof prompt !== "string" || !prompt.trim()) {
    report.errors.push(`${filename}: positive trigger needs a prompt`);
    return;
  }
  if (typeof topK !== "number" || isNaN(topK) || topK < 1) {
    report.errors.push(`${filename}: positive trigger has invalid top_k`);
    return;
  }

  const ranking = rankSkills(prompt, descriptions);
  const index = ranking.findIndex((item) => item.name === expected);
  if (index === -1) {
    report.errors.push(`${expected}: skill not found in ranking`);
    return;
  }
  const hit = ranking[index];
  if (index === 0 && hit.score > 0) {
    report.rankOnePositives++;
  }
  if (index < topK && hit.score > 0) {
    report.routingPassed++;
    return;
  }
  if (hit.score === 0) {
    report.errors.push(
      `${expected}: positive prompt shares no vocabulary with its description: ${JSON.stringify(prompt)}`
    );
    return;
  }
  const leaders = ranking
    .slice(0, 3)
    .filter((item) => item.score > 0)
    .map((item) => `${item.name} (${item.score.toFixed(2)})`)
    .join(", ");
  report.errors.push(
    `${expected}: positive prompt ranked ${index + 1}, expected top ${topK}: ${JSON.stringify(prompt)}; leaders: ${leaders}`
  );
}

export function checkNegative(
  filename: string,
  expected: string,
  trigger: unknown,
  descriptions: Record<string, string>,
  report: EvaluationReport
): void {
  report.routingChecks++;

  if (typeof trigger !== "object" || trigger === null || Array.isArray(trigger)) {
    report.errors.push(`${filename}: negative trigger must be an object`);
    return;
  }
  const t = trigger as Record<string, any>;
  const prompt = t.prompt;
  const owner = t.owner;

  if (typeof prompt !== "string" || !prompt.trim()) {
    report.errors.push(`${filename}: negative trigger needs a prompt`);
    return;
  }
  if (typeof owner !== "string" || !(owner in descriptions)) {
    report.errors.push(`${filename}: negative trigger declares unknown owner ${JSON.stringify(owner)}`);
    return;
  }

  const ranking = rankSkills(prompt, descriptions);
  const selfIndex = ranking.findIndex((item) => item.name === expected);
  const ownerIndex = ranking.findIndex((item) => item.name === owner);

  if (ranking[0].name === expected && ranking[0].score > 0) {
    report.errors.push(
      `${expected}: ranked first for negative prompt owned by ${owner}: ${JSON.stringify(prompt)}`
    );
    return;
  }
  if (ranking[ownerIndex].score === 0 || ownerIndex > selfIndex) {
    report.errors.push(
      `${expected}: owner ${owner} did not outrank it for negative prompt: ${JSON.stringify(prompt)}`
    );
    return;
  }
  report.routingPassed++;
}

export function evaluateRepository(root: string): EvaluationReport {
  const report = new EvaluationReport();
  const descriptions = loadSkillDescriptions(root);
  report.skillCount = Object.keys(descriptions).length;

  const casesDir = path.join(root, "evals", "cases");
  const loadedCases: Array<{ path: string; name: string; data: any }> = [];

  if (fs.existsSync(casesDir)) {
    const caseFiles = fs
      .readdirSync(casesDir)
      .filter((file) => file.endsWith(".json"))
      .sort();

    for (const file of caseFiles) {
      const fullPath = path.join(casesDir, file);
      try {
        const data = JSON.parse(fs.readFileSync(fullPath, "utf-8"));
        loadedCases.push({
          path: fullPath,
          name: file.replace(/\.json$/, ""),
          data,
        });
      } catch (err: any) {
        report.errors.push(`${file}: invalid JSON: ${err.message}`);
      }
    }
  }
  report.caseFiles = loadedCases.length;

  const caseNames = new Set(loadedCases.map((c) => c.name));
  for (const name of Object.keys(descriptions).sort()) {
    if (!caseNames.has(name)) {
      report.warnings.push(`${name}: no routing case file`);
    }
  }

  for (const { name: expected, path: casePath, data } of loadedCases) {
    const filename = path.basename(casePath);
    if (typeof data !== "object" || data === null || Array.isArray(data)) {
      report.errors.push(`${filename}: case file must contain an object`);
      continue;
    }
    if (data.skill_name !== expected) {
      report.errors.push(
        `${filename}: skill_name ${JSON.stringify(data.skill_name)} does not match filename`
      );
    }
    if (!(expected in descriptions)) {
      report.errors.push(`${filename}: no matching skill directory`);
      continue;
    }
    const trigger = data.trigger;
    if (typeof trigger !== "object" || trigger === null || Array.isArray(trigger)) {
      report.errors.push(`${filename}: 'trigger' must be an object`);
      continue;
    }
    const positives = trigger.positive ?? [];
    const negatives = trigger.negative ?? [];
    if (!Array.isArray(positives) || !Array.isArray(negatives)) {
      report.errors.push(`${filename}: positive and negative triggers must be lists`);
      continue;
    }

    for (const positive of positives) {
      checkPositive(filename, expected, positive, descriptions, report);
    }
    for (const negative of negatives) {
      checkNegative(filename, expected, negative, descriptions, report);
    }

    validateBehavioralCases(filename, data.evals ?? [], report);

    const behavioral = data.evals ?? [];
    const behavioralCount = Array.isArray(behavioral) ? behavioral.length : 0;
    if (
      positives.length < MIN_POSITIVE ||
      negatives.length < MIN_NEGATIVE ||
      behavioralCount < MIN_BEHAVIORAL
    ) {
      report.warnings.push(
        `${expected}: below pilot minimums (${positives.length} positive/${negatives.length} negative/${behavioralCount} behavioral)`
      );
    }
  }

  checkCollisions(descriptions, report);
  return report;
}
