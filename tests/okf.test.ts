import { describe, test, expect } from "bun:test";
import {
  parseFrontmatter,
  isValidActor,
  getTrustTier,
  validateConcept,
  formatStageIndex,
  formatMasterIndex,
  formatBundleName,
  type OkfFrontmatter,
  type ConceptDocument,
} from "../scripts/okf.ts";

describe("OKF Frontmatter Parser", () => {
  test("parses valid YAML frontmatter and separates body", () => {
    const raw = `---
type: "Architecture Decision"
title: "Test ADR"
status: "accepted"
date: "2026-10-02"
tags: [test, okf]
---
# Body content
This is the body.`;

    const { frontmatter, body } = parseFrontmatter(raw);
    expect(frontmatter).not.toBeNull();
    expect(frontmatter?.type).toBe("Architecture Decision");
    expect(frontmatter?.title).toBe("Test ADR");
    expect(frontmatter?.status).toBe("accepted");
    expect(frontmatter?.tags).toEqual(["test", "okf"]);
    expect(body.trim()).toBe("# Body content\nThis is the body.");
  });

  test("returns null frontmatter when delimiters are missing", () => {
    const raw = `# Just Markdown
No frontmatter here.`;
    const { frontmatter, body } = parseFrontmatter(raw);
    expect(frontmatter).toBeNull();
    expect(body).toBe(raw);
  });

  test("handles malformed YAML gracefully", () => {
    const raw = `---
type: [unclosed array
---
# Malformed`;
    const { frontmatter, body } = parseFrontmatter(raw);
    expect(frontmatter).toBeNull();
    expect(body).toBe(raw);
  });
});

describe("OKF Actor Convention & Validation", () => {
  test("accepts human actors", () => {
    expect(isValidActor("human:sirius")).toBe(true);
    expect(isValidActor("human:ccwu")).toBe(true);
    expect(isValidActor("human:john.doe")).toBe(true);
  });

  test("accepts agent / model actors", () => {
    expect(isValidActor("agent/thinker")).toBe(true);
    expect(isValidActor("agent/builder")).toBe(true);
    expect(isValidActor("copilot-cli/gemini-3.8-flash")).toBe(true);
  });

  test("accepts process actors", () => {
    expect(isValidActor("process:ci-qualification")).toBe(true);
    expect(isValidActor("process:bun-test")).toBe(true);
  });

  test("rejects invalid actor strings", () => {
    expect(isValidActor("")).toBe(false);
    expect(isValidActor("   ")).toBe(false);
    expect(isValidActor("anonymous")).toBe(false);
    expect(isValidActor("just a name")).toBe(false);
    expect(isValidActor("human:")).toBe(false);
    expect(isValidActor("/model")).toBe(false);
  });
});

describe("OKF Trust Tiers", () => {
  test("classifies draft documents as unverified even if verified field exists", () => {
    const fm: OkfFrontmatter = {
      type: "Requirement",
      status: "draft",
      verified: { by: "human:sirius", at: "2026-10-02" },
    };
    expect(getTrustTier(fm)).toBe("unverified");
  });

  test("classifies unverified when verified field is missing", () => {
    const fm: OkfFrontmatter = {
      type: "Architecture Decision",
      status: "accepted",
    };
    expect(getTrustTier(fm)).toBe("unverified");
  });

  test("classifies human-reviewed when verified by a human", () => {
    const fm: OkfFrontmatter = {
      type: "Architecture Decision",
      status: "accepted",
      verified: { by: "human:sirius", at: "2026-10-02" },
    };
    expect(getTrustTier(fm)).toBe("human-reviewed");
  });

  test("classifies machine-confirmed when verified by an automated process or agent", () => {
    const fm: OkfFrontmatter = {
      type: "Contract",
      status: "stable",
      verified: { by: "process:ci-test-gate", at: "2026-10-02" },
    };
    expect(getTrustTier(fm)).toBe("machine-confirmed");
  });

  test("supports multiple verifications where human overrides machine", () => {
    const fm: OkfFrontmatter = {
      type: "Architecture Decision",
      status: "accepted",
      verified: [
        { by: "process:ci-gate", at: "2026-10-02" },
        { by: "human:sirius", at: "2026-10-02" },
      ],
    };
    expect(getTrustTier(fm)).toBe("human-reviewed");
  });
});

describe("Concept Document Validation", () => {
  test("identifies missing required fields", () => {
    const fm: OkfFrontmatter = {};
    const issues = validateConcept("test.md", fm);
    const fields = issues.map((i) => i.field);
    expect(fields).toContain("type");
    expect(fields).toContain("status");
    expect(fields).toContain("title");
    expect(fields).toContain("description");
  });

  test("validates status values", () => {
    const fm: OkfFrontmatter = {
      type: "Requirement",
      status: "invalid_status",
    };
    const issues = validateConcept("test.md", fm);
    expect(issues.some((i) => i.field === "status" && i.message.includes("Invalid status"))).toBe(true);
  });

  test("validates ISO dates and actor formats", () => {
    const fm: OkfFrontmatter = {
      type: "Requirement",
      status: "accepted",
      date: "not-a-date",
      generated: { by: "invalid-actor", at: "bad-date" },
      verified: { by: "invalid-actor-2" },
    };
    const issues = validateConcept("test.md", fm);
    const errors = issues.filter((i) => i.severity === "error");
    expect(errors.some((i) => i.field === "date")).toBe(true);
    expect(errors.some((i) => i.field === "generated.by")).toBe(true);
    expect(errors.some((i) => i.field === "generated.at")).toBe(true);
    expect(errors.some((i) => i.field === "verified.by")).toBe(true);
  });

  test("warns when superseded document lacks superseded_by", () => {
    const fm: OkfFrontmatter = {
      type: "Architecture Decision",
      status: "superseded",
      title: "Old Decision",
      description: "An old superseded decision.",
    };
    const issues = validateConcept("test.md", fm);
    expect(issues.some((i) => i.field === "superseded_by")).toBe(true);
  });

  test("passes valid document with zero errors", () => {
    const fm: OkfFrontmatter = {
      type: "Architecture Decision",
      id: "ADR-008",
      title: "ADR-008: Open Knowledge Format",
      description: "Adopts OKF for progressive disclosure.",
      status: "accepted",
      date: "2026-10-02",
      generated: { by: "human:sirius", at: "2026-10-02" },
      verified: { by: "human:sirius", at: "2026-10-02" },
    };
    const issues = validateConcept("test.md", fm);
    const errors = issues.filter((i) => i.severity === "error");
    expect(errors.length).toBe(0);
  });
});

describe("OKF Index Formatting & Bundle Naming", () => {
  test("formats stage index with progressive disclosure entries", () => {
    const mockDocs: ConceptDocument[] = [
      {
        filePath: "/path/to/docs/decisions/adr-008.md",
        relativePath: "adr-008.md",
        frontmatter: {
          id: "ADR-008",
          title: "ADR-008: OKF Adoption",
          description: "Adopts OKF progressive disclosure.",
          status: "accepted",
          verified: { by: "human:sirius" },
        },
        rawContent: "",
        body: "",
      },
    ];

    const output = formatStageIndex("Decisions", "Architecture Decision Records", mockDocs);
    expect(output).toContain("okf_version: \"0.2\"");
    expect(output).toContain("# Decisions");
    expect(output).toContain("* [ADR-008: OKF Adoption](adr-008.md) - Adopts OKF progressive disclosure. `[accepted | human-reviewed]`");
  });

  test("formats master index linking stages", () => {
    const stages = [
      { name: "Stage 1", dir: "requirements", desc: "User stories", count: 2 },
      { name: "Stage 2", dir: "contracts", desc: "Operation contracts", count: 1 },
    ];
    const output = formatMasterIndex(stages, "Thinker");
    expect(output).toContain("okf_version: \"0.2\"");
    expect(output).toContain("# Thinker Knowledge Bundle (OKF v0.2)");
    expect(output).toContain("* [**Stage 1**](requirements/index.md) (2 concepts) - User stories");
    expect(output).toContain("* [**Stage 2**](contracts/index.md) (1 concepts) - Operation contracts");
  });

  test("formats bundle names accurately", () => {
    expect(formatBundleName("thinker")).toBe("Thinker");
    expect(formatBundleName("foxpilot")).toBe("FoxPilot");
    expect(formatBundleName("my-service")).toBe("My-service");
    expect(formatBundleName("")).toBe("Knowledge Bundle");
  });
});
