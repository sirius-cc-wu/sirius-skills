import { describe, expect, test } from "bun:test";
import { stem, tokenize, countTerms, rankSkills } from "../scripts/evals/nlp";

describe("nlp", () => {
  test("stem handles suffix rules correctly", () => {
    expect(stem("practically")).toBe("practic");
    expect(stem("testing")).toBe("test");
    expect(stem("loaded")).toBe("load");
    expect(stem("classes")).toBe("clas");
    expect(stem("historical")).toBe("historic");
    expect(stem("skills")).toBe("skil");
    expect(stem("address")).toBe("addres");
    expect(stem("create")).toBe("creat");
    expect(stem("stopping")).toBe("stop");
    expect(stem("quality")).toBe("qualiti");
  });

  test("tokenize removes punctuation, stop words, and short tokens", () => {
    const tokens = tokenize("I need help with reviewing the Pull-Request!");
    // "reviewing" -> "review", "pull" -> "pull", "request" -> "request"
    expect(tokens).toEqual(["review", "pull", "request"]);
  });

  test("tokenize preserves tokens whose unstemmed length was > 2", () => {
    const tokens = tokenize("doing dishes");
    expect(tokens).toEqual(["doing", "dish"]);
  });

  test("rankSkills uses names and descriptions and scores correctly", () => {
    const descriptions = {
      "publish-change": "Publish a prepared repository change.",
      "architecture-map": "Map components, runtime collaborations, deployment, and dependencies.",
    };
    const ranking = rankSkills(
      "Reconstruct the deployed components and runtime dependencies",
      descriptions
    );

    expect(ranking[0].name).toBe("architecture-map");
    expect(ranking[0].score).toBeGreaterThan(0);
    expect(ranking[1].name).toBe("publish-change");
  });
});
