# Plan

**Status (2026-10-16):** Annotation redesign is not a planned effort this quarter. After two maintainer meetings the team decided against adopting it now, because there is no clear path and rushing risks repeating the mistakes that produced the current surface. The team did agree on the [declarative resource modeling principles](https://github.com/hashicorp/terraform-provider-aws/blob/main/docs/design-decisions/declarative-resource-modeling-principles.md), and liked the list-resource spike (typed Go declarations driving a shared implementation). Work proceeds as small independent pieces, each worth doing on its own even if the larger redesign is never adopted, building consensus one piece at a time. Public tracking: [issue 50242](https://github.com/hashicorp/terraform-provider-aws/issues/50242).

Options are in [options/](../options/README.md); the measurements behind them are in [findings/](../findings/README.md).

## Decisions

- **No planned redesign this quarter.** No clear path, and the team does not want to rush into a similar mistake.
- **Principles agreed and merged.** The [principles doc](https://github.com/hashicorp/terraform-provider-aws/blob/main/docs/design-decisions/declarative-resource-modeling-principles.md) now constrains any future option; see [ruled-out.md](../options/ruled-out.md) for what it eliminates.
- **Ship small, independent pieces.** Each piece below stands alone. Consensus is built piece by piece, not by ratifying a whole design up front.
- **The list-resource spike is the model to follow.** Typed Go declarations consumed by a shared implementation, proven byte-identical on three resources ([list-resource-experiment](../findings/list-resource-experiment.md)).

## Pieces, in order

Each is worth doing even if nothing else here lands.

**1. Fix the `tagsTests` typo.** `internal/service/elasticache/reserved_cache_node.go:37` reads `@Testing(tagsTests=false)`; the key is `tagsTest`. No generator reads `tagsTests`, so the opt-out does nothing and nothing flags it ([silent-failures](../findings/silent-failures.md)). One-line fix.
Done when: the line reads `tagsTest=false` (or the annotation is removed if the opt-out was never intended) and `make gen PKG=elasticache` is clean.

**2. Characterization tests for the `servicepackage` generator.** The generator was refactored in September and has no tests; 28 of 29 generator directories have none ([generators](../findings/generators.md)). Golden tests pin today's output so any later parser change is verifiable, and they guard against regressions on their own.
Done when: `go test ./internal/generate/servicepackage/...` passes over synthetic-service fixtures (shaped like the simple, structured, and exception running examples in [options](../options/README.md)) and fails on a deliberate one-line template change. Include one negative fixture recording today's silent unknown-key behavior.

**3. Normalize list-resource flatten functions, then land the Shape A shared implementation.** `*Flatten` functions carry three return contracts across 130 functions; roughly 95 are not on the `error` contract ([list-resource-experiment](../findings/list-resource-experiment.md)). Normalizing to `error` composes with smarterr, the provider's stated direction, and is cleanup worth doing with or without the shared implementation. With the contract uniform, the spike's single generic implementation replaces per-resource bodies for Shape A (paginate and flatten each item), about 53 files, break-even near the fourth resource.
Done when: the targeted flatten functions return `error`; the converted Shape A resources compile and pass their list acceptance tests; registration stays byte-identical after `make gen`. Normalization can ship as its own PR before the shared implementation.

**4. Remove `existsType` on comprehend's two resources.** `document_classifier.go` and `entity_recognizer.go` author only `existsType` and `preCheck`, no crossing keys. Replace the string-named Go type with a type argument in the generated exists-check. A wrong derived type is a compile error in generated code in the same package, not a silent failure ([exists-type](../findings/exists-type.md)), so compiling verifies it. `existsType` is the single largest key, so this also measures whether the mechanism generalizes.
Done when: both resources drop `existsType`, the package compiles, its unit tests pass, and one acceptance run per resource passes (with approval, since it creates AWS resources).

**5. Report-only unknown-key and liveness checker.** A command that walks `internal/service` and prints unknown annotation keys, marker-looking lines that fail the regex, and test-generation keys in services whose `generate.go` never runs that generator. Report-only, no enforcement yet. It names the live problems without committing to a representation. Expected output includes the `tagsTests` typo and the known inert opt-out lines ([silent-failures](../findings/silent-failures.md)).
Done when: the checker runs across the tree and its output is recorded. Turning it into a `make gen` error waits on piece 2 and on seeing the fallout.

## Kept

- **Classify the 121 services that have `@Tags` but do not run `tagstests`** (deliberate, omitted, or missing fixtures). Needed by piece 5: the liveness checker must not report a service as inert when it only lacks fixtures ([testing-keys](../findings/testing-keys.md)).

## Parked

Each returns when its condition holds.

- **Registration redesign** (deriving the public type name, authored-literal versus directive forms, factory discovery). Returns if a derivation with a loud-failing rule is proven, or the team decides to take the redesign on.
- **Move `@Testing` to `_test.go` as a pilot.** Returns if the team decides a relocation counts as the migration unit and accepts relaxing the `_test.go` exclusion in the generator walker ([generators](../findings/generators.md)).
- **`make resource-info` generated report.** Returns if discoverability becomes the blocking disagreement again; it supplies a per-concern view without moving authority ([resource-report](../options/resource-report.md)).
- **The judgment calls**, none settled by measurement: explicit type name versus zero authoring; whether an authored literal is too dense to review; whether facts live with the resource or with the concern; whether uniformity across plugin frameworks is required. Each returns when a piece forces it or a maintainer decides it ([criteria](../options/criteria.md)).

## Cut

- **Derive the friendly `Name` for all entries** and **ask the constructed object at startup** about Import, Region, and Tags presence. Both feed registration, which is parked, so neither is worth running now. A wrong `Name` would silently relocate 685 fixture directories ([silent-failures](../findings/silent-failures.md)), which is also why its derivation is not a safe standalone piece.

## Open decisions

- **When report-only checks become `make gen` errors.** Enforcement waits on piece 2 covering the parser and on the report-only fallout being known.
- **How far to normalize flatten functions** beyond what Shape A needs (the remaining ~95). Scope question for piece 3.
- **Whether the criteria tiers are ever formally ratified** ([criteria](../options/criteria.md)). Piece-by-piece consensus may make a single vote unnecessary.
