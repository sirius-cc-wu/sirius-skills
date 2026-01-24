---
name: branch-uml-diagrams
description: Finds important changes in the current branch against its merge-base with main, and creates before and after PlantUML files in the relevant spec folders, guided by the spec-driver skill for finding spec files. It also checks the syntax of the generated PlantUML files.
---

# Branch UML Diagram Generator

This skill analyzes the current branch, identifies significant code changes against the merge-base with the `main` branch, and generates PlantUML diagrams to visualize the architecture before and after the modifications. It uses the spec-driver skill's guidance to locate the appropriate specification file.

## Workflow

### 1. Get Branch Changes

This skill compares the current branch with its merge-base with the `main` branch to identify changes. This is useful for preparing a pull request.

First, save the current branch name:
```bash
git rev-parse --abbrev-ref HEAD > current_branch.txt
```

Then, get the diff between the merge-base and the current branch (`HEAD`):
```bash
git diff $(git merge-base main HEAD)..HEAD --color "never" > branch.diff
```

This will give you the raw diff to analyze.

### 2. Identify Important Changes

Analyze the `branch.diff` file to identify significant changes. Focus on modifications to source code files (e.g., `.rs`, `.py`, `.js`, `.ts`). Look for:

-   New or deleted files.
-   Changes to function or method signatures.
-   Modifications to class or struct definitions.
-   Addition or removal of significant blocks of logic.

For each file with an important change, you will generate a pair of UML diagrams.

### 3. Find Corresponding Spec File

For each changed file, you must locate its corresponding `spec.md` file. This can be done by:
1.  First, inspect `specs/README.md` to identify the active track or tracks relevant to the changed component.
2.  Then, within the identified track's directory (e.g., `specs/<track_id>/`), look for `spec.md`.
3.  If a direct match isn't found, you may need to infer the relevant track based on the changed file's path and the existing track structures.

### 4. Generate "Before" UML Diagram

1.  **Checkout the merge-base commit:**
    ```bash
    git checkout $(git merge-base main HEAD)
    ```
2.  **Analyze the code:** Read the contents of the file as it existed on the merge-base commit. Identify the relevant classes, structs, functions, and their relationships.
3.  **Write PlantUML:** Create a new file named `<filename>_before.puml` in the same directory as the spec file. Write the PlantUML syntax to describe the code's structure. For a syntax reference, consult `references/plantuml-cheatsheet.md`.
4.  **Check Syntax:** Use the `plantuml` command with the `-checkonly` flag to check the syntax of the PlantUML file. This will not generate an image file.
    ```bash
    plantuml -checkonly <spec_directory>/<filename>_before.puml
    ```

### 5. Generate "After" UML Diagram

1.  **Checkout the original branch:**
    ```bash
    git checkout $(cat current_branch.txt)
    ```
2.  **Analyze the code:** Read the contents of the file on the current branch.
3.  **Write PlantUML:** Create a `<filename>_after.puml` file and write the the new PlantUML description.
4.  **Check Syntax:** Use the `plantuml` command with the `-checkonly` flag to check the syntax of the PlantUML file.
    ```bash
    plantuml -checkonly <spec_directory>/<filename>_after.puml
    ```

### 6. Finalize Diagrams

The generated UML diagrams (`.puml` files) are placed in the same directory as the corresponding `spec.md` file. No futher action is needed.

### 7. Cleanup

After generating diagrams for all important changes, clean up intermediate files.
```bash
rm branch.diff current_branch.txt
```
The workflow ensures you are back on your original branch.
