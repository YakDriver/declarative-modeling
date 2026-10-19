# The problem with the provider's annotations

The Terraform AWS provider registers every resource and configures its tests with comment annotations: one marker per resource, plus keyword arguments for tags, region, identity, import, and test generation. That surface has grown to 7,025 lines ([inventory](findings/surface.md)), it accepts plainly wrong keys without a word, and the write cost the design was meant to save is no longer the cost that matters.

## What an annotation is

A resource carries one comment line above its factory:

```go
// @SDKResource("aws_ecs_service", name="Service")
func resourceService() *schema.Resource {
```

A generator reads the comment and writes the registration entry into `service_package_gen.go`. Run `make gen PKG=ecs`, and the resource is registered. Every later need took the same home: tags, region, identity, import, test generation, version history. The full inventory and how it spreads across files is in [findings/surface.md](findings/surface.md).

## How it got here

The design did not arrive whole. The first form, in early 2023, was four bare markers with no keyword arguments at all. The keyword-argument sub-language came six weeks later for `@Tags`, and every key since, including all 54 `@Testing` keys and the behavior of silently ignoring unknown keys, lives in a facility added after the design shipped, for a different marker. The surface was nearly flat for about nine months, then grew 2.75x since April 2024, with `@Testing` about half of that. Timeline, quoted motivations, and the growth curve are in [findings/history.md](findings/history.md).

## Do the original motivations still hold

Annotations answered four recorded concerns: merge conflicts on a central registration file, a circular dependency between the provider and its resources, the style guide's ban on `init()` registries, and per-resource boilerplate. Coding agents weaken only the last. Agents type lines cheaply, so write cost deserves less weight than it used to. But review has not gotten cheaper (a human still reads every authored line), and agents write plausible wrong keys that comment syntax never rejects.

## Four costs, not one

An annotation design trades between four things, and they do not move together:

- **Write**: lines a developer or agent produces.
- **Review**: facts a human must check.
- **Concepts**: things a contributor must learn before writing anything.
- **Density**: lines per fact.

Review and density come apart for a typed literal. `Factory:`, `TypeName:`, and `Name:` look like three facts, but `Factory: resourceService` is a binding the machinery requires, not a fact, and `Region: inttypes.ResourceRegionDefault()` carries no resource-specific information in the 88% of entries that say it ([findings/registration.md](findings/registration.md)). A reviewer reads past binding and default syntax to find the one or two values that actually vary. So "what is irreducible?" is a different question from "comments or Go?"

## Which job is the problem

The markers do four different jobs with different ages and growth (line counts as of 2026-10-01, from [findings/surface.md](findings/surface.md)):

- **Registration** (2,679 lines) is the original bare-marker design and grows with the resource count.
- **Tags and region** feed registration fields and trigger generated tag tests.
- **Identity and import** (894 lines) arrived in 2025 and expand into thousands of nested generated lines.
- **Test generation** (`@Testing`, 2,275 lines) carries most of the recent growth and most of the keyword-argument language, yet produces none of its own output. It configures the other generators.

Registration is the simplest syntax; `@Testing` and identity are where the complexity sits. Of the `@Testing` keyword occurrences, 51.2% are history, switches, environment, or execution policy, which a running program cannot supply ([findings/testing-keys.md](findings/testing-keys.md)). The single largest key, `existsType`, names a Go type the type system already holds ([findings/exists-type.md](findings/exists-type.md)). Deciding which job to change first is an open question, because the jobs have different problems. See [../concepts/derive-before-authoring.md](../concepts/derive-before-authoring.md).

## One name doing two jobs

`Name` is a diagnostic label at runtime (error messages) and a filesystem key at generation time, selecting the `testdata/` fixture directory that generated tag and identity tests point at. Deriving `Name` from the Go identifier is possible for most resources, but a wrong derivation would move those fixture directories and point generated tests at a path that does not exist. That is one reason a derivation that guesses silently is worse than an authored value. See [../concepts/divergence-is-not-configuration.md](../concepts/divergence-is-not-configuration.md).

## Facts that constrain every option

Any redesign has to live with these, regardless of syntax:

- The jobs are entangled: some `@Testing` keys ship in the binary, others fail `make gen` while appearing in no generated file ([findings/provider-contract.md](findings/provider-contract.md)).
- Wrong keys and malformed lines are silent. One live key in use, `tagsTests`, is a typo that no generator reads and nothing flags ([findings/silent-failures.md](findings/silent-failures.md)).
- The public type name is not a unique key: 552 type names register more than once (a resource and a data source, or aliases like `aws_alb`/`aws_lb`). The identifying tuple is (kind, type name).
- Source filenames and `Name` are generator inputs, so moving metadata out of a resource's file changes derived paths unless the binding is explicit. See [../concepts/declaration-placement.md](../concepts/declaration-placement.md).

## What is irreducible

For a non-aliased, conventionally shaped resource whose kind can be identified reliably, the authored information not obtainable elsewhere in the code may be a single string: the public type name. That type name already exists as a docs filename and in sweeper registrations, so it is one fact written in several places under any design. The qualifiers are real and none is yet satisfied: factory discovery is unproven, aliased resources need at least two strings, and "conventionally shaped" has no rule that fails loud. The larger differences between options sit in the 58% of entries with structured metadata and in `@Testing`. See [../concepts/what-must-survive.md](../concepts/what-must-survive.md).

## Where to go next

- [findings/](findings/) measurements of the current surface: size, growth, keys, derivability, silent failures, the runtime contract.
- [options/](options/) the design options under consideration and the ones ruled out.
- [plan/](plan/plan.md) what is decided and what happens next.
