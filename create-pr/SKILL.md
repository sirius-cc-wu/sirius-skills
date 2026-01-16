---
name: create-pr
description: Creates GitHub pull requests with properly formatted titles that pass the check-pr-title CI validation. Use when creating PRs, submitting changes for review, or when the user says /pr or asks to create a pull request.
allowed-tools: Bash(git:*), Bash(gh:*), Read, Grep, Glob
---

# Create Pull Request

Creates GitHub PRs with titles that pass the `check-pr-title` CI validation.

## PR Title Format

```
<JIRA-ID>: <summary>
```

### JIRA-ID

The JIRA-ID is extracted from the current branch name. Branch names follow the format:
```
XXXX-nnnn-description-of-work
```

Where:
- `XXXX` = 3 or 4 uppercase English characters (project key)
- `nnnn` = 4-digit issue number

**Examples:**
| Branch Name | JIRA-ID |
|-------------|---------|
| `B1XF-3916-optimize-m-core-init-process` | `B1XF-3916` |
| `FDC-1234-add-new-feature` | `FDC-1234` |
| `BSP-5678-fix-memory-leak` | `BSP-5678` |

### Summary Rules

- Use imperative present tense: "Add" not "Added"
- Capitalize first letter
- No period at the end
- Be concise but descriptive

## Steps

1. **Check current state**:
   ```bash
   git status
   git diff --stat
   git log origin/main..HEAD --oneline
   ```

2. **Extract JIRA-ID from branch name**:
   ```bash
   BRANCH=$(git rev-parse --abbrev-ref HEAD)
   JIRA_ID=$(echo "$BRANCH" | grep -oE '^[A-Z]{3,4}-[0-9]{4}')
   echo "JIRA-ID: $JIRA_ID"
   ```

3. **Analyze changes** to determine:
   - Summary: What does the change do?

4. **Push branch if needed**:
   ```bash
   git push -u origin HEAD
   ```

5. **Create PR** using gh CLI:
   ```bash
   BRANCH=$(git rev-parse --abbrev-ref HEAD)
   JIRA_ID=$(echo "$BRANCH" | grep -oE '^[A-Z]{3,4}-[0-9]{4}')
   gh pr create --draft --title "${JIRA_ID}: <summary>" --body "$(cat <<'EOF'
   ## Description

   <Describe what the PR does and how to test. Photos and videos are recommended.>

   Fixes # <JIRA-ID>

   ## Type of change

   - [ ] Bug fix
   - [ ] New feature
   - [ ] Improvement
   - [ ] Breaking change

   ## How Has This Been Tested?

   - [ ] Unit tests
   - [ ] Integration tests
   - [ ] Manual testing

   ## Checklist:

   - [ ] My code follows the style guidelines of this project
   - [ ] I have performed a self-review of my own code
   - [ ] I have commented my code, particularly in hard-to-understand areas
   - [ ] I have made corresponding changes to the documentation
   - [ ] New and existing unit tests pass locally with my changes
   - [ ] I have checked my code and corrected any misspellings
   EOF
   )"
   ```

## PR Body Guidelines

### Description Section
- Describe what the PR does
- Explain how to test the changes
- Include screenshots/videos for UI changes
- Reference the JIRA ticket with `Fixes # <JIRA-ID>`

### Type of Change
Select the appropriate type:
- Bug fix - Fixes an issue
- New feature - Adds new functionality
- Improvement - Enhances existing functionality
- Breaking change - Changes that break backward compatibility

### Testing Section
Describe how the changes were tested

### Checklist
All items should be addressed before merging

## Examples

### Optimization change
```
B1XF-3916: Optimize M-core initialization process
```

### Bug fix
```
FDC-1234: Fix memory leak in UDS handler
```

### New feature
```
BSP-5678: Add DTC status reporting API
```

### Refactoring
```
B1XF-2345: Refactor DID configuration structure
```

## Validation

The PR title must match this pattern:
```
^[A-Z]{3,4}-[0-9]{4}: [A-Z].+[^.]$
```

Key validation rules:
- JIRA-ID must be 3-4 uppercase letters followed by hyphen and 4 digits
- Colon and space after JIRA-ID
- Summary must start with capital letter
- Summary must not end with a period
