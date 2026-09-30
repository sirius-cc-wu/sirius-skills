import * as path from "node:path";

export const STOP_WORDS = new Set([
  "a",
  "an",
  "and",
  "are",
  "as",
  "at",
  "be",
  "before",
  "by",
  "for",
  "from",
  "help",
  "i",
  "in",
  "into",
  "is",
  "it",
  "its",
  "me",
  "my",
  "need",
  "needs",
  "of",
  "on",
  "or",
  "our",
  "so",
  "that",
  "the",
  "them",
  "this",
  "to",
  "use",
  "want",
  "we",
  "when",
  "with",
  "you",
  "your",
]);

export interface RankedSkill {
  name: string;
  score: number;
}

export type TermFrequency = Map<string, number>;

export function stem(token: string): string {
  let result = token;
  for (const suffix of ["ally", "ing", "ed", "es", "al"]) {
    if (result.length > suffix.length + 3 && result.endsWith(suffix)) {
      result = result.slice(0, -suffix.length);
      break;
    }
  }
  if (result.length > 3 && result.endsWith("s") && !result.endsWith("ss")) {
    result = result.slice(0, -1);
  }
  if (result.length > 4 && result.endsWith("e")) {
    result = result.slice(0, -1);
  }
  if (
    result.length > 4 &&
    result[result.length - 1] === result[result.length - 2] &&
    !"aeiou".includes(result[result.length - 1])
  ) {
    result = result.slice(0, -1);
  }
  if (result.length > 3 && result.endsWith("y")) {
    result = `${result.slice(0, -1)}i`;
  }
  return result;
}

export function tokenize(text: string): string[] {
  const raw = text.toLowerCase().replace(/[^a-z0-9\s-]/g, " ");
  const rawTokens = raw.split(/[\s-]+/);
  const tokens: string[] = [];

  for (const token of rawTokens) {
    if (token.length > 2 && !STOP_WORDS.has(token)) {
      tokens.push(stem(token));
    }
  }

  return tokens;
}

export function countTerms(tokens: string[]): TermFrequency {
  const counts = new Map<string, number>();
  for (const token of tokens) {
    counts.set(token, (counts.get(token) || 0) + 1);
  }
  return counts;
}

export function skillTerms(name: string, description: string): TermFrequency {
  const nameTokens = tokenize(name.replace(/-/g, " "));
  const descTokens = tokenize(description);
  return countTerms([...nameTokens, ...nameTokens, ...descTokens]);
}

export function idf(term: string, documents: TermFrequency[]): number {
  let frequency = 0;
  for (const doc of documents) {
    if (doc.has(term)) {
      frequency++;
    }
  }
  return Math.log(1 + documents.length / (1 + frequency));
}

export function tfidfVector(terms: TermFrequency, documents: TermFrequency[]): Map<string, number> {
  const vector = new Map<string, number>();
  for (const [term, count] of terms.entries()) {
    vector.set(term, count * idf(term, documents));
  }
  return vector;
}

export function cosineSimilarity(left: Map<string, number>, right: Map<string, number>): number {
  let dot = 0.0;
  let leftNormSq = 0.0;
  for (const [term, weight] of left.entries()) {
    dot += weight * (right.get(term) || 0.0);
    leftNormSq += weight * weight;
  }
  let rightNormSq = 0.0;
  for (const weight of right.values()) {
    rightNormSq += weight * weight;
  }
  const leftNorm = Math.sqrt(leftNormSq);
  const rightNorm = Math.sqrt(rightNormSq);
  if (!leftNorm || !rightNorm) {
    return 0.0;
  }
  return dot / (leftNorm * rightNorm);
}

export function rankSkills(prompt: string, descriptions: Record<string, string>): RankedSkill[] {
  const names = Object.keys(descriptions).sort();
  const termCounts = new Map<string, TermFrequency>();
  for (const name of names) {
    termCounts.set(name, skillTerms(name, descriptions[name]));
  }
  const documents = Array.from(termCounts.values());
  const promptVector = tfidfVector(countTerms(tokenize(prompt)), documents);

  const ranking: RankedSkill[] = names.map((name) => {
    const docVector = tfidfVector(termCounts.get(name)!, documents);
    const score = cosineSimilarity(promptVector, docVector);
    return { name, score };
  });

  return ranking.sort((a, b) => {
    if (b.score !== a.score) {
      return b.score - a.score;
    }
    return a.name.localeCompare(b.name);
  });
}
