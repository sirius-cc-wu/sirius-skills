---
name: use-case
description: A skill for creating detailed use case specifications for features.
---

# Use Case Specification Skill

This skill is designed to create detailed use case specifications, providing a structured way to describe the interactions between users (actors) and a system. It is ideal for situations where a more formal and comprehensive specification is required than a user story.

## Core Components of a Use Case

A use case created with this skill will include the following sections, based on the provided `assets/use-case-template.md`:

-   **Goal**: The overall objective of the use case.
-   **Actors**: The users or systems involved.
-   **Preconditions**: Conditions that must be met before the use case can start.
-   **Main Success Scenario**: The "happy path" of the interaction.
-   **Alternative Flows & Extensions**: Different paths and error conditions.
-   **Postconditions**: The state of the system after the use case is completed.
-   **Test Cases**: Scenarios to test the use case.
-   **Supporting Information**: Business rules, glossary, etc.

## Workflow for Elaboration

This skill is used to elaborate on an existing user story within a `spec.md` file. The track should already be initialized.

1.  **Identify Target Story**: The user specifies which user story from the `spec.md` needs to be elaborated into a use case.
2.  **Create Use Case File**: A new file named `use-case-<story-name>.md` is created in the same `specs/<ID>-<name>/` directory.
3.  **Copy the Template**: Copy the content of `assets/use-case-template.md` into the new file.
4.  **Fill out the Template**: Work with the user to fill out all the sections of the use case template.
5.  **Link to Spec**: Add a link in the original `spec.md` under the relevant user story, pointing to the new use case file (e.g., `Detailed Use Case: [use-case-<story-name>.md](use-case-<story-name>.md)`).
6.  **Finalize the Specification**: Once all sections are complete, the use case file is ready.
