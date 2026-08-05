---
type: "Architecture Decision"
title: "Opaque Reference Matcher Boundary"
description: "Preserve the existing public matcher boundary for reconciliation comparison."
id: "DESIGN-MATCH-PORT"
revision: "D-5"
status: "active"
tags: ["design", "boundary"]
---

# Opaque Reference Matcher Boundary

The platform design authority approved revision `D-5` for the matching slice.
Use the existing public boundary
`ReconciliationMatcher.compare(first, second) -> MatchResult`.

`MatchResult` already permits the states `same-account`, `different-account`,
and `invalid-reference`, plus the two supplied opaque references and an optional
invalid-input position. It permits no protected customer attributes and owns no
persistence. This decision does not authorize a new service, schema, queue, or
customer lookup.
