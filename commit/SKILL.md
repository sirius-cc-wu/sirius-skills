---
name: commit
description: Guide for creating commit messages that track changes effectively and follow project standards.
---

# Commit Standards

This skill provides guidance for creating commit messages.

## Critical Rules

### 1. Escape Backticks
**Constraint:** You MUST escape backticks (\`) with a backslash (\\) in commit messages.
**Reason:** Unescaped backticks can break build scripts or changelog generators that parse git history.

*   **Wrong:** `feat: add `FileTransferHandler` struct`
*   **Right:** `feat: add \`FileTransferHandler\` struct`

## Best Practices

### Conventional Commits
Unless otherwise specified, follow [Conventional Commits](https://www.conventionalcommits.org/):
`type(scope): description`

*   `feat`: New feature
*   `fix`: Bug fix
*   `docs`: Documentation only changes
*   `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
*   `refactor`: A code change that neither fixes a bug nor adds a feature
*   `perf`: A code change that improves performance
*   `test`: Adding missing tests or correcting existing tests
*   `chore`: Changes to the build process or auxiliary tools and libraries such as documentation generation

### Specificity
Be specific about what changed and why.

## Workflow

1.  **Stage Changes:** Use `git add <files>`.
2.  **Draft Message:** Prepare your message, ensuring backticks are escaped.
3.  **Commit:** Execute `git commit -m "your message"`.
