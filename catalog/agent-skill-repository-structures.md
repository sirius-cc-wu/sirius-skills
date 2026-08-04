---
type: "Recovered Architecture"
title: "Agent-Skill Repository Structure and Relationship Comparison"
description: "Compares the structures and documented skill-to-skill handoffs of two agent-skill repositories."
status: "completed"
revisions:
  - "addyosmani/agent-skills@98967c45a42b88d6b8fb3a88b7ff6273920763d6"
  - "garrytan/gstack@7c9df1c568a9ea745508f679a329332b2c338063"
tags: ["reverse-engineering", "architecture", "plantuml", "skill-repositories"]
---

# Agent-Skill Repository Structure and Relationship Comparison

## At a glance

These repositories all distribute agent skills, but the repository plays a
different role in each system:

- `addyosmani/agent-skills` is a hand-authored, multi-host content bundle. Its
  skills, commands, personas, hooks, and checklists are separate composable
  layers.
- `garrytan/gstack` is both a generated skill distribution and an executable
  product. Templates and host configuration produce skill documents that call
  a substantial browser, design, document, memory, and installation runtime.

The consequence is that similarly named `SKILL.md` repositories have very
different change surfaces. Addy's structure emphasizes parallel host adapters,
while gstack emphasizes generation and runtime coupling.

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

In the two structural diagrams:

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

## Structural comparison

| Dimension | `addyosmani/agent-skills` | `garrytan/gstack` |
|---|---|---|
| Canonical authoring unit | Hand-authored `skills/<name>/SKILL.md` package | `SKILL.md.tmpl` plus generated sections, resolvers, code metadata, and host configuration |
| Primary organizing axis | Software-delivery phase, supplemented by personas and commands | Specialist workflow/tool at the repository root |
| Orchestration | Eight lifecycle commands select skills; `/ship` additionally fans out to three personas | Generated skill prose embeds shared preambles and tool instructions; skills directly invoke runtime helpers |
| Cross-host strategy | Parallel command formats and several plugin/directory adapters over one skill catalog | Typed host configurations transform content, frontmatter, paths, tools, metadata, and installation behavior |
| Executable runtime | Light: validation/eval scripts, hooks, and one optional skill helper | Heavy: compiled TypeScript and shell tools, a persistent browser daemon, browser extension, local state, remote pairing, and other product subsystems |
| Publication boundary | The active catalog is broadly distributed; command variants are kept in parity | Host configurations can include, skip, rewrite, or suppress skill content per host |
| Checked verification surface | Skill schema/reference checks, command parity checks, deterministic routing cases, and optional behavioral evals | Generated-file freshness, skill command validation, unit/integration tests, host E2E tests, and LLM evaluation tiers |
| Main extension seam | Add a skill, persona, reference, hook, or synchronized command adapter | Add or change a template, resolver, host config, runtime component, or test tier |

### Interpretation

The following conclusions are inferences from the structures above rather than
statements of project intent:

1. **Addy's repository favors explicit composition.** Skills, commands,
   personas, and references can evolve independently, while validators carry
   the cost of keeping mirrored host commands synchronized.
2. **gstack favors centralized adaptation.** Its generator and typed host
   configuration reduce manual host-by-host editing, but the generator, setup
   system, runtime assets, and tests form a much larger coupled change surface.

## Skill relationship views

These are workflow maps, not source-code dependency graphs. A solid arrow means
a documented normal sequence or handoff. A dashed arrow means an optional route,
a reusable discipline, or runtime support. The Addy Osmani view shows all 24
skills. The larger gstack view stays bounded to documented handoffs and names
isolated utilities without inventing relationships for them.

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

## Skill-relationship comparison

| Dimension | `addyosmani/agent-skills` | `garrytan/gstack` |
|---|---|---|
| Primary router | `using-agent-skills` selects a lifecycle skill | `autoplan` sequences planning reviewers; several other skills orchestrate specialist clusters |
| Main delivery shape | A mostly linear define-plan-build-verify-review-ship spine with optional specializations | A product-delivery spine surrounded by tool-backed design, browser, safety, deployment, and platform loops |
| Reuse mechanism | Phase-specific skills are composed by commands and selected when risk warrants | Skills invoke other skills and shared executable runtimes; plan artifacts are handed to later skills |
| Feedback loops | Debugging returns to regression testing; simplification returns to review | Live design/DevEx review follows planning; QA and canary feed fixes back before or after shipping |
| Relationship authority | Explicit routing and example sequences in the meta-skill and command docs | README sprint model plus orchestration encoded in generated skill templates |
| Coverage choice here | All 24 skills | Documented connected workflows plus named independent utilities; not an exhaustive catalog |

## Evidence and limits

| Repository | Primary structural and relationship evidence | Claim status |
|---|---|---|
| `addyosmani/agent-skills` | [`README.md` project structure](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/README.md#L323-L359), [`using-agent-skills` router](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/skills/using-agent-skills/SKILL.md), [`AGENTS.md` composition rules](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/AGENTS.md), [Claude plugin manifest](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/.claude-plugin/plugin.json), [command validator](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/scripts/validate-commands.js), and [eval runner](https://github.com/addyosmani/agent-skills/blob/98967c45a42b88d6b8fb3a88b7ff6273920763d6/scripts/run-evals.js) | Structural and relationship claims corroborated, high confidence, current at recorded revision |
| `garrytan/gstack` | [`ARCHITECTURE.md`](https://github.com/garrytan/gstack/blob/7c9df1c568a9ea745508f679a329332b2c338063/ARCHITECTURE.md), [`README.md` sprint model](https://github.com/garrytan/gstack/blob/7c9df1c568a9ea745508f679a329332b2c338063/README.md), [`autoplan` template](https://github.com/garrytan/gstack/blob/7c9df1c568a9ea745508f679a329332b2c338063/autoplan/SKILL.md.tmpl), [skill generator](https://github.com/garrytan/gstack/blob/7c9df1c568a9ea745508f679a329332b2c338063/scripts/gen-skill-docs.ts), [host registry](https://github.com/garrytan/gstack/blob/7c9df1c568a9ea745508f679a329332b2c338063/hosts/index.ts), and [host configuration contract](https://github.com/garrytan/gstack/blob/7c9df1c568a9ea745508f679a329332b2c338063/scripts/host-config.ts) | Structural claims high confidence; relationship view bounded to explicit handoffs and support paths, current at recorded revision |

This compares repository modules, distribution boundaries, and documented
workflow relationships; it does not claim observed runtime behavior. No
installer, agent host, browser daemon, paid evaluation, or external service was
executed. Generated, dependency, vendor, build-output, and runtime-state trees
were excluded except where their existence defines an architectural boundary.
