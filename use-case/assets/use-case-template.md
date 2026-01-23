# Use Case: [Use Case Title]

**Goal**: [A brief, user-centric description of the goal]

**Actors**:
- **Primary Actor**: [The user or system that initiates the use case]
- **Supporting Actors**: [Other users or systems involved]

---

## Preconditions

*   [A condition that must be true before the use case begins]
*   [Another condition, if applicable]

---

## Main Success Scenario (Happy Path)

1.  **Actor**: [Performs an action]
2.  **System**: [Responds to the action]
3.  **Actor**: [Performs another action]
4.  **System**: [Responds and completes the use case]

---

## Alternative Flows & Extensions

### 3a. [Name of the alternative scenario]

*   **At step 3** of the main scenario, if [condition for the alternative path is met]:
    1.  **System**: [Does something different]
    2.  [The flow continues, and may either rejoin the main flow or end here]

### 4a. [Name of an error scenario]

*   **At step 4** of the main scenario, if [an error condition occurs]:
    1.  **System**: [Handles the error gracefully]
    2.  **System**: [Provides feedback to the actor]

---

## Postconditions

*   **On Success**: [The state of the system if the main success scenario is completed]
*   **On Failure**: [The state of the system if the use case fails]

---

## Test Cases

*   **Test Case 1**: [Description of a test case to verify the main success scenario]
*   **Test Case 2**: [Description of a test case to verify an alternative flow or error condition]

---

## Supporting Information

*   **Glossary**:
    *   **[Term]**: [Definition]
*   **Business Rules**:
    *   [A specific rule that applies to this use case]
*   **Non-Functional Requirements**:
    *   **Performance**: [e.g., The system must respond within 2 seconds]
    *   **Security**: [e.g., All data must be encrypted at rest]
