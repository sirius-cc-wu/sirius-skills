# Playbook 7: Prototype Spike (Throwaway Exploration)

**Trigger:** Novel UI layout, interaction feel, or stateful workflow with no codebase precedent.
**Alpha Progression:** *Requirements* → *Bounded (Exploratory)*.

## Steps

1. **Scope the Decision**
   - Define the exact layout, interaction feel, or stateful workflow being decided.
   - **Constraint:** Strict scratch isolation (`<appDataDir>/scratch/prototypes/<name>/` or `scratch/prototypes/`). Zero production code changes.

2. **Build Competing Sketches**
   - Implement 2–3 competing approaches (*Option A*, *Option B*, *Option C*) behind a single on-screen variant switcher using `prototype-spike` (vanilla HTML/CSS/JS or the lightest static setup).

3. **Observe & Capture Evidence**
   - Test interaction feel across target viewports via browser tools. Capture side-by-side screenshots.

4. **Human Review & Handover**
   - Present options and trade-offs to the operator for decision.
   - Discard scratch code upon sign-off, extract the chosen specification and tokens, and transition to **Playbook 2 (Feature Slice)** or **Playbook 1 (Architectural)** for production implementation.
