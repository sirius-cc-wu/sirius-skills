---
type: "Recovered Architecture"
title: "Agent-Skill Repository Structure and Relationship Comparison"
description: "Compares the structures and documented skill-to-skill handoffs of Addy Osmani's agent-skills, gstack, and Sirius skills."
status: "completed"
revisions:
  - "addyosmani/agent-skills@98967c45a42b88d6b8fb3a88b7ff6273920763d6"
  - "garrytan/gstack@7c9df1c568a9ea745508f679a329332b2c338063"
  - "sirius-skills@1420ab11d763119a0e6217f906257a8db3441c10"
tags: ["reverse-engineering", "architecture", "plantuml", "skill-repositories"]
---

# Agent-Skill Repository Structure and Relationship Comparison

## At a glance

These repositories all distribute agent skills, but each repository plays a
different role:

- `addyosmani/agent-skills` is a hand-authored, multi-host content bundle. Its
  skills, commands, personas, hooks, and checklists are separate composable
  layers.
- `garrytan/gstack` is both a generated skill distribution and an executable
  product. Templates and host configuration produce skill documents that call
  browser, design, document, memory, and installation runtimes.
- `sirius-skills` is a profile-driven collection of independently deployable
  workflow skills. Its catalog, tracks, shared references, installers, and
  tests govern how the skills compose. It has no product runtime.

The same `SKILL.md` shape therefore hides different change surfaces. Addy's
structure emphasizes host adapters. gstack emphasizes generation and runtime
coupling. Sirius emphasizes catalog boundaries, profile ownership, and
risk-sized workflow composition.

## Question, scope, and notation

The architectural questions are: **How does each repository separate canonical
skill authoring, orchestration, distribution or runtime support, and
verification?** And: **How do its documented skills hand off work to one
another?** The diagrams use those common views so their differences are
comparable.

The source trees and documentation were inspected read-only at the revisions in
the frontmatter. Each checkout was clean and its local `main` matched its local
`origin/main` tracking reference. No network fetch was performed, so “current”
means the local revision recorded here, not an assertion about the latest remote
commit.

In the three structural diagrams:

- a solid arrow is a direct generation, packaging, invocation, or runtime path;
- a dashed arrow is supporting content, policy, or an optional path;
- blue packages contain canonical authoring sources;
- green packages contain orchestration or transformation;
- purple packages contain distribution surfaces;
- orange packages contain executable runtime elements; and
- yellow packages contain documentation or verification surfaces.

## Addy Osmani's `agent-skills`

The canonical unit is a hand-authored skill directory. Host-specific commands
sit above the skill catalog, while specialist personas provide an independent
review role that commands such as `/ship` can fan out to. Plugin manifests and
plain-directory integrations expose the same underlying content to several
agent hosts.

```plantuml
@startuml addyosmani-agent-skills-structure
left to right direction

skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam packageStyle rectangle
skinparam componentStyle rectangle
skinparam linetype ortho
skinparam defaultFontName Arial
skinparam ArrowColor #52606D
skinparam component {
  BackgroundColor #FFFFFF
  BorderColor #52606D
}

actor "AI coding-agent host" as addyHost

package "Canonical content" #EAF4FB {
  component "skills/\n24 workflow packages" as addySkills
  component "agents/\n4 specialist personas" as addyAgents
  component "references/\n7 shared checklists" as addyReferences
}

package "Orchestration" #EEF8EE {
  component "8 lifecycle commands\nClaude: .claude/commands/*.md\nGemini: .gemini/commands/*.toml\nAntigravity: commands/*.toml" as addyCommands
  component "hooks/session-start.sh\nmeta-skill injection" as addyHook
}

package "Distribution" #F3EEFF {
  component ".claude-plugin/\nmanifest + marketplace" as addyClaudePlugin
  component ".codex-plugin/\nmanifest" as addyCodexPlugin
  component "plugin.json + .opencode/skills\nplain Markdown / skills CLI" as addyOtherAdapters
}

package "Documentation and verification" #FFFBEA {
  component "README.md + docs/" as addyDocs
  component "validate-skills.js\nvalidate-commands.js" as addyValidators
  component "evals/cases/ + run-evals.js\n24 skill-routing cases" as addyEvals
}

addyCommands --> addySkills : invokes workflows
addyCommands --> addyAgents : /ship fan-out
addyAgents ..> addySkills : may apply workflows
addySkills ..> addyReferences : loads when needed
addyHook --> addySkills : injects using-agent-skills

addyHost --> addyClaudePlugin : install / invoke
addyHost --> addyCodexPlugin : install / invoke
addyHost --> addyOtherAdapters : install / discover
addyClaudePlugin --> addySkills : exposes
addyClaudePlugin --> addyCommands : exposes
addyClaudePlugin --> addyAgents : exposes
addyCodexPlugin --> addySkills : exposes
addyOtherAdapters --> addySkills : exposes
addyOtherAdapters --> addyCommands : host-specific entry points

addyDocs ..> addySkills : catalogs and explains
addyDocs ..> addyAgents : catalogs and explains
addyValidators --> addySkills : structure and references
addyValidators --> addyCommands : cross-host parity
addyEvals --> addySkills : routing and behavior checks
@enduml
```

## Garry Tan's `gstack`

The canonical skill prose lives in templates, not the committed generated
`SKILL.md` files. A generator combines those templates with shared resolvers,
runtime command metadata, and declarative host configuration. The installed
skills then call executable helpers; the persistent Chromium daemon is the
largest runtime collaboration but not the only compiled tool in the repository.

```plantuml
@startuml gstack-structure
top to bottom direction

skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam packageStyle rectangle
skinparam componentStyle rectangle
skinparam linetype ortho
skinparam defaultFontName Arial
skinparam ArrowColor #52606D
skinparam component {
  BackgroundColor #FFFFFF
  BorderColor #52606D
}

actor "Maintainer" as gstackMaintainer
actor "AI coding-agent host" as gstackHost

package "Canonical authoring sources" #EAF4FB {
  component "SKILL.md.tmpl + sections/*.md.tmpl\n55 generator-discovered skill templates\n+ 16 on-demand section templates" as gstackTemplates
  component "scripts/resolvers/ + runtime metadata\nshared and code-derived skill content" as gstackResolvers
  component "hosts/*.ts\n10 declarative host configs" as gstackHostConfigs
  component "Runtime source\nbrowse/src, design/src, make-pdf/src, bin/" as gstackRuntimeSource
}

package "Generation and installation" #EEF8EE {
  component "scripts/gen-skill-docs.ts" as gstackGenerator
  component "scripts/build.sh\nBun compilation and assets" as gstackBuild
  component "setup\nhost detection + link/copy strategy" as gstackSetup
}

package "Distribution" #F3EEFF {
  component "Committed Claude SKILL.md files" as gstackClaudeDocs
  component "Generated host-specific skill trees\nCodex, OpenCode, Factory, Kiro,\nCursor, Slate, OpenClaw, Hermes, GBrain" as gstackExternalDocs
  component "Installed host skill directories\nglobal or repository-local" as gstackInstalled
}

package "Executable runtime" #FFF5EA {
  component "Compiled and shell helpers\nbrowse, design, PDF, iOS, memory, release" as gstackHelpers
  component "Browse CLI" as gstackBrowseCli
  component "Long-lived local HTTP daemon\nBun.serve" as gstackDaemon
  component "Chromium\nPlaywright / CDP" as gstackChromium
  database "Workspace and user state\n.gstack + ~/.gstack" as gstackState
}

package "Documentation and verification" #FFFBEA {
  component "ARCHITECTURE.md + docs/" as gstackDocs
  component "skill-check + generation freshness\n+ Bun unit, integration, host E2E, and LLM evals" as gstackChecks
}

gstackMaintainer --> gstackTemplates : edits
gstackMaintainer --> gstackRuntimeSource : edits
gstackTemplates --> gstackGenerator
gstackResolvers --> gstackGenerator
gstackHostConfigs --> gstackGenerator : transforms per host
gstackRuntimeSource --> gstackGenerator : command metadata
gstackRuntimeSource --> gstackBuild
gstackGenerator --> gstackClaudeDocs : committed output
gstackGenerator --> gstackExternalDocs : adapted output
gstackHostConfigs --> gstackSetup : paths and policy
gstackSetup --> gstackGenerator : generates as needed
gstackSetup --> gstackInstalled : links or copies
gstackClaudeDocs --> gstackInstalled
gstackExternalDocs --> gstackInstalled
gstackBuild --> gstackHelpers
gstackSetup --> gstackHelpers : installs runtime assets

gstackHost --> gstackInstalled : discovers and invokes
gstackInstalled --> gstackHelpers : runs $B and other tools
gstackHelpers --> gstackBrowseCli
gstackBrowseCli --> gstackDaemon : localhost HTTP
gstackDaemon --> gstackChromium : CDP
gstackDaemon --> gstackState : session and logs

gstackDocs ..> gstackTemplates : explains workflows
gstackDocs ..> gstackRuntimeSource : explains runtime design
gstackChecks --> gstackGenerator : freshness and command validity
gstackChecks --> gstackSetup
gstackChecks --> gstackHelpers
gstackChecks --> gstackDaemon
@enduml
```

## Sirius skills

The canonical unit is an independently deployable `skills/<name>/` package.
Profiles select convenient combinations. The catalog and tracks define
responsibilities and handoffs. Shared references have one source under
`docs/shared/` and are copied into the packages that use them. Installation
uses the profiles and host-skill tooling; the package has no product runtime.

```plantuml
@startuml sirius-skills-structure
left to right direction

skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam packageStyle rectangle
skinparam componentStyle rectangle
skinparam linetype ortho
skinparam defaultFontName Arial
skinparam ArrowColor #52606D
skinparam component {
  BackgroundColor #FFFFFF
  BorderColor #52606D
}

actor "Maintainer" as siriusMaintainer
actor "AI coding-agent host" as siriusHost

package "Canonical content" #EAF4FB {
  component "skills/\n30 workflow packages" as siriusSkills
  component "skill-sets/\nprofiles + all.txt" as siriusProfiles
  component "catalog/\nskills, tracks, relationships" as siriusCatalog
  component "docs/shared/\ncanonical references" as siriusReferences
  component "docs/ideas/\nidea and historical artifacts" as siriusIdeas
}

package "Packaging and installation" #EEF8EE {
  component "justfile + npx skills\nprofile install/uninstall" as siriusInstall
  component "src/sirius_skills/commands/\nsync + ownership management" as siriusTools
  component "host-local managed state" as siriusState
}

package "Distribution" #F3EEFF {
  component "Global or workspace\nagent skill directories" as siriusInstalled
}

package "Documentation and verification" #FFFBEA {
  component "README.md + AGENTS.md + PROMPT_GUIDE.md\nusage, rules, and prompts" as siriusDocs
  component "scripts/validate_skills.sh\nshared-reference checks" as siriusValidator
  component "evals/cases/ + routing runner" as siriusEvals
  component "pytest tests" as siriusTests
}

siriusMaintainer --> siriusSkills : edits
siriusMaintainer --> siriusCatalog : defines boundaries
siriusMaintainer --> siriusProfiles : selects composition
siriusMaintainer --> siriusDocs : documents rules
siriusMaintainer --> siriusIdeas : records candidate directions
siriusCatalog --> siriusSkills : describes and routes
siriusProfiles --> siriusInstall : selects packages
siriusReferences --> siriusSkills : copied to consumers
siriusInstall --> siriusInstalled : installs profiles
siriusTools --> siriusInstall : syncs and manages
siriusTools --> siriusState : records ownership
siriusHost --> siriusInstalled : discovers and invokes
siriusDocs ..> siriusCatalog : explains composition
siriusDocs ..> siriusIdeas : explains artifact paths
siriusValidator --> siriusSkills : structure and references
siriusValidator --> siriusProfiles : membership checks
siriusEvals --> siriusSkills : routing checks
siriusTests --> siriusTools : behavior checks
@enduml
```

## Structural comparison

| Dimension | `addyosmani/agent-skills` | `garrytan/gstack` | `sirius-skills` |
|---|---|---|---|
| Canonical authoring unit | Hand-authored `skills/<name>/SKILL.md` package | `SKILL.md.tmpl` plus generated sections, resolvers, code metadata, and host configuration | Hand-authored `skills/<name>/SKILL.md` package plus profile, catalog, and track guidance |
| Primary organizing axis | Software-delivery phase, supplemented by personas and commands | Specialist workflow/tool at the repository root | Risk-sized questions, workflow tracks, and profile composition |
| Orchestration | Lifecycle commands select skills; `/ship` fans out to personas | Generated skill prose embeds shared preambles and tool instructions; skills invoke runtime helpers | Content-based intake, recovery and discovery tracks, and one risk-driven development coordinator |
| Cross-host strategy | Parallel command formats and several plugin/directory adapters over one skill catalog | Typed host configurations transform content, frontmatter, paths, tools, metadata, and installation behavior | Profiles install selected packages through `npx skills`; shared references are synchronized into consuming packages |
| Executable runtime | Light: validation/eval scripts, hooks, and one optional skill helper | Heavy: compiled TypeScript and shell tools, a persistent browser daemon, browser extension, local state, remote pairing, and other product subsystems | No product runtime; packaging, ownership, synchronization, and validation commands support the skill collection |
| Publication boundary | The active catalog is broadly distributed; command variants are kept in parity | Host configurations can include, skip, rewrite, or suppress skill content per host | `skill-sets/all.txt` and named profiles own active membership; host-local state records successful ownership |
| Checked verification surface | Skill schema/reference checks, command parity checks, deterministic routing cases, and optional behavioral evals | Generated-file freshness, skill command validation, unit/integration tests, host E2E tests, and LLM evaluation tiers | `just validate`, `pytest`, deterministic routing evals, catalog/profile checks, and managed-installation tests |
| Main extension seam | Add a skill, persona, reference, hook, or synchronized command adapter | Add or change a template, resolver, host config, runtime component, or test tier | Add a skill specialist, profile/catalog/track boundary, shared reference, packaging rule, or focused eval |

### Interpretation

The following conclusions are inferences from the structures above rather than
statements of project intent:

1. **Addy Osmani's repository favors explicit composition.** Skills, commands,
   personas, and references can evolve independently, while validators carry
   the cost of keeping mirrored host commands synchronized.
2. **gstack favors centralized adaptation.** Its generator and typed host
   configuration reduce manual host-by-host editing, but the generator, setup
   system, runtime assets, and tests form a much larger coupled change surface.
3. **Sirius favors profile-driven composition.** Its skills remain small and
   independently deployable, while the catalog, profiles, shared references,
   installation tooling, and verification surfaces keep the collection
   coherent. It has less runtime coupling than gstack and more catalog and
   packaging governance than Addy's bundle.

## Skill relationship views

These are workflow maps, not source-code dependency graphs. A solid arrow means
a documented normal sequence or handoff. A dashed arrow means an optional route,
a reusable discipline, or runtime support. The Addy Osmani view shows all 24
skills. The gstack view stays bounded to documented handoffs and names isolated
utilities without inventing relationships for them. The Sirius view shows its
intake, recovery, discovery, risk-driven development, and repository-workflow
boundaries without repeating every specialist edge.

### Addy Osmani: lifecycle router and delivery path

`using-agent-skills` is the catalog router. Its documented full-project path
provides the central spine; specializations and quality passes attach where the
task or risk calls for them. The shorter bug-fix path rejoins the spine at
test-driven development and review.

```plantuml
@startuml addyosmani-skill-relationships
top to bottom direction

skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam packageStyle rectangle
skinparam componentStyle rectangle
skinparam linetype ortho
skinparam defaultFontName Arial
skinparam ArrowColor #52606D
skinparam component {
  BackgroundColor #FFFFFF
  BorderColor #52606D
}

component "using-agent-skills\nworkflow router" as addyUsing #FFF2CC

package "Define" as addyDefine #EAF4FB {
  component "interview-me" as addyInterview
  component "idea-refine" as addyIdea
  component "spec-driven-development" as addySpec
}

package "Plan" as addyPlanPhase #EEF8EE {
  component "planning-and-task-breakdown" as addyPlan
}

package "Build" as addyBuild #F3EEFF {
  component "incremental-implementation" as addyIncremental
  component "context-engineering" as addyContext
  component "source-driven-development" as addySource
  component "doubt-driven-development" as addyDoubt
  component "frontend-ui-engineering" as addyFrontend
  component "api-and-interface-design" as addyApi
}

package "Verify" as addyVerify #FFF5EA {
  component "test-driven-development" as addyTdd
  component "browser-testing-with-devtools" as addyBrowser
  component "debugging-and-error-recovery" as addyDebug
}

package "Review" as addyReviewPhase #FFFBEA {
  component "code-review-and-quality" as addyReview
  component "code-simplification" as addySimplify
  component "security-and-hardening" as addySecurity
  component "performance-optimization" as addyPerformance
}

package "Integrate and ship" as addyShipPhase #F2F2F2 {
  component "git-workflow-and-versioning" as addyGit
  component "ci-cd-and-automation" as addyCi
  component "deprecation-and-migration" as addyDeprecation
  component "documentation-and-adrs" as addyDocsSkill
  component "observability-and-instrumentation" as addyObservability
  component "shipping-and-launch" as addyShipping
}

addyUsing ..> addyDefine : routes discovery
addyUsing ..> addyPlanPhase : routes planning
addyUsing ..> addyBuild : routes implementation
addyUsing ..> addyVerify : routes failures and tests
addyUsing ..> addyReviewPhase : routes quality checks
addyUsing ..> addyShipPhase : routes integration and release

addyInterview --> addyIdea
addyIdea --> addySpec
addySpec --> addyPlan
addyPlan --> addyContext
addyContext --> addySource
addySource --> addyIncremental
addyIncremental --> addyDoubt : challenge risky changes
addyDoubt --> addyTdd : tested slices
addyTdd --> addyReview
addyReview --> addySimplify
addySimplify --> addyGit
addyGit --> addyDocsSkill
addyDocsSkill --> addyDeprecation
addyDeprecation --> addyShipping

addyIncremental ..> addyFrontend : UI specialization
addyIncremental ..> addyApi : interface specialization
addyIncremental ..> addyObservability : instrument in parallel

addyTdd ..> addyBrowser : browser-facing behavior
addyDebug --> addyTdd : regression test
addySimplify ..> addyReview : re-review
addyReview ..> addySecurity : risk warrants
addyReview ..> addyPerformance : evidence warrants
addyTdd ..> addyCi : automate checks

addyCi ..> addyShipping
addyObservability ..> addyShipping
@enduml
```

### Garry Tan: delivery spine and specialist clusters

gstack documents a delivery spine from product thinking through planning,
review, QA, shipping, deployment, and monitoring. `autoplan` orchestrates the
planning reviews. Browser-backed, design, safety, iOS, memory, and publishing
skills form reusable clusters around that spine.

```plantuml
@startuml gstack-skill-relationships
top to bottom direction

skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam packageStyle rectangle
skinparam componentStyle rectangle
skinparam linetype ortho
skinparam defaultFontName Arial
skinparam ArrowColor #52606D
skinparam component {
  BackgroundColor #FFFFFF
  BorderColor #52606D
}

package "Delivery spine" as gDelivery #EAF4FB {
  component "office-hours" as gOffice
  component "spec" as gSpec
  component "autoplan" as gAutoplan
  component "plan-ceo-review" as gPlanCeo
  component "plan-design-review" as gPlanDesign
  component "plan-eng-review" as gPlanEng
  component "plan-devex-review" as gPlanDevex
  component "review" as gReview
  component "qa" as gQa
  component "ship" as gShip
  component "setup-deploy" as gSetupDeploy
  component "land-and-deploy" as gLand
  component "canary" as gCanary
  component "document-release" as gDocRelease
  component "document-generate" as gDocGenerate
}

package "Design and live review" as gDesign #EEF8EE {
  component "design-consultation" as gDesignConsult
  component "design-shotgun" as gDesignShotgun
  component "design-html" as gDesignHtml
  component "design-review" as gDesignReview
  component "devex-review" as gDevexReview
}

package "Browser-backed workflows" as gBrowserGroup #F3EEFF {
  component "browse" as gBrowse
  component "open-gstack-browser" as gOpenBrowser
  component "setup-browser-cookies" as gBrowserCookies
  component "pair-agent" as gPairAgent
  component "qa-only" as gQaOnly
  component "benchmark" as gBenchmark
  component "scrape" as gScrape
  component "skillify" as gSkillify
}

package "Safety and diagnosis" as gSafety #FFF5EA {
  component "careful" as gCareful
  component "freeze" as gFreeze
  component "guard" as gGuard
  component "unfreeze" as gUnfreeze
  component "investigate" as gInvestigate
  component "cso" as gCso
  component "codex" as gCodex
}

package "iOS quality loop" as gIos #FFFBEA {
  component "ios-qa" as gIosQa
  component "ios-fix" as gIosFix
  component "ios-design-review" as gIosDesign
  component "ios-sync" as gIosSync
  component "ios-clean" as gIosClean
}

package "Context, memory, and publishing" as gContext #F2F2F2 {
  component "context-save" as gContextSave
  component "context-restore" as gContextRestore
  component "setup-gbrain" as gSetupGbrain
  component "sync-gbrain" as gSyncGbrain
  component "diagram" as gDiagram
  component "make-pdf" as gMakePdf
  component "Other documented utilities\nlearn, retro, health, benchmark-models, plan-tune,\nlanding-report, gstack-upgrade" as gUtilities
}

gOffice --> gSpec : settle intent
gOffice --> gPlanCeo : design doc
gOffice ..> gAutoplan : full planning pass
gSpec ..> gAutoplan : expand plan
gSpec ..> gPlanEng : direct plan review

gAutoplan --> gPlanCeo
gPlanCeo ..> gPlanDesign : UI work
gPlanCeo --> gPlanEng
gPlanDesign --> gPlanEng
gPlanEng ..> gPlanDevex : developer-facing work
gPlanEng --> gReview : after implementation
gPlanEng --> gQa : test plan
gReview --> gQa
gReview --> gShip : fixes verified
gQa --> gShip
gSpec ..> gShip : closes source issue
gSetupDeploy ..> gLand : configures
gShip --> gLand
gLand --> gCanary
gShip ..> gDocRelease
gLand ..> gDocRelease
gDocRelease ..> gDocGenerate : documentation gaps

gDesignConsult ..> gDesignShotgun : established system
gDesignShotgun --> gDesignHtml
gPlanDesign ..> gDesignShotgun : explore alternatives
gPlanDesign ..> gDesignHtml : prototype
gPlanDesign --> gDesignReview : live follow-up
gPlanDevex --> gDevexReview : live follow-up

gOpenBrowser --> gBrowse : headed mode
gBrowserCookies ..> gBrowse : authenticated sessions
gPairAgent ..> gBrowse : remote collaboration
gBrowse ..> gQa
gBrowse ..> gQaOnly
gBrowse ..> gDesignReview
gBrowse ..> gDevexReview
gBrowse ..> gBenchmark
gBrowse ..> gCanary
gBrowse ..> gScrape
gScrape --> gSkillify : make repeatable

gGuard --> gCareful
gGuard --> gFreeze
gInvestigate --> gFreeze : preserve evidence
gFreeze --> gUnfreeze
gCodex ..> gReview : cross-model comparison

gIosQa --> gIosFix : found defects
gIosQa ..> gIosDesign : visual audit
gIosQa ..> gIosSync : bridge upkeep
gIosQa --> gIosClean : release cleanup

gContextSave --> gContextRestore
gSetupGbrain --> gSyncGbrain
gDiagram --> gMakePdf : render source
@enduml
```

### Sirius: intake to risk-driven delivery

Sirius uses content-based intake and a separate recovery track. A single
risk-driven coordinator selects the needed specialists, including native
responsibility design and the Rust lifecycle specialist when ownership or
resource semantics create material pressure. For boundary-sensitive
refactorings, the coordinator retains the system boundary, representative
vertical oracle, responsibility assignment, ownership consequences,
verification ownership, and parent completion boundary. The same coordinator
owns implementation, verification, continuous iteration, and
one-commit-per-iteration execution.

```plantuml
@startuml sirius-skill-relationships-comparison
left to right direction

skinparam backgroundColor #FFFFFF
skinparam shadowing false
skinparam packageStyle rectangle
skinparam componentStyle rectangle
skinparam linetype ortho
skinparam defaultFontName Arial
skinparam ArrowColor #52606D
skinparam component {
  BackgroundColor #FFFFFF
  BorderColor #52606D
}

package "Intake" #FFF2CC {
  component "assess-development-input" as sAssess
}

package "Understand the system" #EAF4FB {
  component "reverse-engineer-software-system" as sReverse
  component "survey-existing-system" as sSurvey
  component "recover-system-behavior" as sBehavior
  component "reconstruct-software-architecture" as sArchitecture
  component "reconcile-recovered-design" as sReconcile
}

package "Risk-driven development" #EEF8EE {
  component "iterative-risk-driven-development" as sIterative
  component "analysis, responsibility,\nand design specialists" as sDesign
  component "design-rust-lifecycles\nwhen Rust pressure is material" as sRust
}

package "Repository workflow" #F3EEFF {
  component "create-pr" as sPr
}

package "Cross-cutting support" #FFFBEA {
  component "select-technical-artifacts" as sSelect
  component "design-repository-artifact-layout" as sLayout
  component "record-architecture-decision" as sAdr
}

sAssess ..> sReverse : current system needs evidence
sAssess ..> sIterative : approved change needs progress
sReverse --> sSurvey
sSurvey ..> sBehavior
sSurvey ..> sArchitecture
sBehavior ..> sReconcile
sArchitecture ..> sReconcile
sReconcile --> sIterative : validated knowledge
sIterative ..> sSelect : artifact choice
sIterative ..> sLayout : placement choice
sIterative ..> sAdr : consequential decision
sIterative ..> sDesign : boundary and responsibilities
sIterative ..> sRust : Rust lifecycle pressure
sRust ..> sDesign : ownership feedback
sIterative --> sPr : committed work
@enduml
```

## Skill-relationship comparison

| Dimension | `addyosmani/agent-skills` | `garrytan/gstack` | `sirius-skills` |
|---|---|---|---|
| Primary router | `using-agent-skills` selects a lifecycle skill | `autoplan` sequences planning reviewers; several other skills orchestrate specialist clusters | `assess-development-input` routes by content; tracks and the risk-driven coordinator manage handoffs |
| Main delivery shape | A mostly linear define-plan-build-verify-review-ship spine with optional specializations | A product-delivery spine surrounded by tool-backed design, browser, safety, deployment, and platform loops | Intake, recovery, risk-driven development, and repository workflow; each risk-sized iteration can continue until the requested work is complete |
| Reuse mechanism | Phase-specific skills are composed by commands and selected when risk warrants | Skills invoke other skills and shared executable runtimes; plan artifacts are handed to later skills | Skills link to narrow specialists, profiles compose packages, and shared references are packaged into consuming skills |
| Feedback loops | Debugging returns to regression testing; simplification returns to review | Live design/DevEx review follows planning; QA and canary feed fixes back before or after shipping | Recovery reconciliation, ownership-to-responsibility feedback, parent-outcome checks, design/implementation feedback, and continuous iteration return evidence to canonical artifacts |
| Relationship authority | Explicit routing and example sequences in the meta-skill and command docs | README sprint model plus orchestration encoded in generated skill templates | Catalog, workflow tracks, skill boundaries, and profile membership |
| Coverage choice here | All 24 skills | Documented connected workflows plus named independent utilities; not an exhaustive catalog | All 26 active skills, with bounded tracks and profile-driven installation |

## Evidence and limits

| Repository | Primary structural and relationship evidence | Claim status |
|---|---|---|
| `addyosmani/agent-skills` | [`README.md` project structure](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/README.md#L323-L359), [`using-agent-skills` router](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/skills/using-agent-skills/SKILL.md), [`AGENTS.md` composition rules](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/AGENTS.md), [Claude plugin manifest](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/.claude-plugin/plugin.json), [command validator](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/scripts/validate-commands.js), and [eval runner](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/scripts/run-evals.js) | Structural and relationship claims corroborated, high confidence, current at recorded revision |
| `garrytan/gstack` | [`ARCHITECTURE.md`](https://github.com/garrytan/gstack/blob/7c9df1c568a9ea745508f679a329332b2c338063/ARCHITECTURE.md), [`README.md` sprint model](https://github.com/garrytan/gstack/blob/7c9df1c568a9ea745508f679a329332b2c338063/README.md), [`autoplan` template](https://github.com/garrytan/gstack/blob/7c9df1c568a9ea745508f679a329332b2c338063/autoplan/SKILL.md.tmpl), [skill generator](https://github.com/garrytan/gstack/blob/7c9df1c568a9ea745508f679a329332b2c338063/scripts/gen-skill-docs.ts), [host registry](https://github.com/garrytan/gstack/blob/7c9df1c568a9ea745508f679a329332b2c338063/hosts/index.ts), and [host configuration contract](https://github.com/garrytan/gstack/blob/7c9df1c568a9ea745508f679a329332b2c338063/scripts/host-config.ts) | Structural claims high confidence; relationship view bounded to explicit handoffs and support paths, current at recorded revision |
| `sirius-skills` | [`README.md`](../README.md), [`AGENTS.md`](../AGENTS.md), [`catalog/skills.md`](skills.md), [`catalog/skill-relationships.md`](skill-relationships.md), [`skill-sets/all.txt`](../skill-sets/all.txt), [`scripts/validate_skills.sh`](../scripts/validate_skills.sh), [`src/sirius_skills/commands/`](../src/sirius_skills/commands/), and [`tests/`](../tests/) | Structural and relationship claims corroborated, high confidence, current at recorded revision `1420ab1` |

This compares repository modules, distribution boundaries, and documented
workflow relationships; it does not claim observed runtime behavior. No
installer, agent host, browser daemon, paid evaluation, or external service was
executed. Generated, dependency, vendor, build-output, and runtime-state trees
were excluded except where their existence defines an architectural boundary.
