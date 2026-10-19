# Criteria for judging an annotation replacement

Fourteen criteria for comparing ways to author the provider's resource metadata. Unweighted they settle nothing: most options win about half and lose about half, so the choice falls to unstated preference. The tiers below are a proposed fix, not a ratified one. Where people disagree on a tier is what decides which experiment result would change a decision.

Each criterion has a plain name here instead of a number. "What it requires" is the test an option either passes or fails.

| Criterion | What it requires | Tier |
|---|---|---|
| Fails early, locally, and never inertly | Invalid declarations are machine-checked for shape, value, and cross-field constraints; the error names the authored line; nothing authored sits with no active consumer. Threshold below. | Hard constraint |
| Serves every consumer | Generators, `skaff`, templates, provider code, docs, and skills all still get their data. | Hard constraint |
| Migrates incrementally | Old and new forms coexist; no big-bang rewrite of every resource at once. | Hard constraint |
| Resource-scoped work stays complete and fast | Authoring, review, debugging, and provider-wide changes stay scoped; registering one resource needs no provider-wide regeneration or hidden cleanup. | Hard constraint |
| Provider keeps getting what it consumes | The running provider receives the same registration values it reads today ([provider-contract](../findings/provider-contract.md)). | Hard constraint |
| Keeps jobs separate and change contained | Registration, tags, identity/import, and testing each change and validate on their own; adding a concern doesn't extend a shared vocabulary or touch unrelated consumers; removing one removes its machinery. | Architectural goal |
| Deletes inferable data instead of moving it | Data recoverable elsewhere in the code is removed, not relocated. See [derive-before-authoring](../../concepts/derive-before-authoring.md). | Architectural goal |
| One definition, one authority, checked copies | One definition of what each item means, one source owning each value, and every other copy generated from that source or cross-checked against it. | Architectural goal |
| Generators don't know individual resources | Generators encode no per-resource knowledge. | Architectural goal |
| Generator ordering lives in code | Ordering between generators is expressed in code, not Makefile sequence plus a comment. | Architectural goal |
| Declaration sits next to its factory | The authored declaration lives in the same file as the factory it describes (per-resource proximity; see [locality](../../concepts/locality.md)). | Preference |
| Stays within generate and build budget | Scoped `make gen` (about 5 s for `ecs`) and full `make gen` don't get materially slower, and Go build and test compile scope don't grow ([registration](../findings/registration.md)). | Preference |
| Easy to write and review | Writable from `skaff`, readable in a diff. | Preference |
| Discoverable per resource and per concern | A developer can enumerate a resource's knobs without reading a generator, and can see one concern across resources. A per-concern view can be generated; per-concern authority competes with co-location. | Preference |

## The fail-early threshold

"Fails early, locally, and never inertly" is the one hard constraint the status quo violates, so it gets a two-part threshold.

1. **No silent error.** No authored error lands at "never", and the error names the authored file and line. Today unknown keys land at "never": `@Testing(tagsTests=false)` at `elasticache/reserved_cache_node.go:37` is a typo for `tagsTest` and is dropped without a warning ([silent-failures](../findings/silent-failures.md)).
2. **No inert configuration.** An authored item with no active consumer in its scope is reported, checked both directions: a test-generation key in a service whose `generate.go` never runs that generator, and a factory nobody registered.

Part 2 is why an unknown-key check alone doesn't clear the bar. It catches `tagsTests`, but not a correctly spelled `tagsTest=false` in a service that never runs the tag-test generator. The ladder from editor to compiler to `make gen` to CI to startup is compared as a goal: earlier is better. The threshold only requires that an error reach a human somewhere short of "never".

## The tiers are proposed, not agreed

The filter works as described only once maintainers accept the tiers. Two refinements are on the table:

- **"One definition, one authority, checked copies" could be hard in the steady state,** with temporary duplication allowed during migration. It stays a goal for now, because its "checked copies" part would disqualify every current option: none checks the `TypeName` copies in sweeper registrations and docs filenames ([provider-contract](../findings/provider-contract.md)). Promoting it is a scope decision about reaching into `sweep.go` and `website/`, not a filter.
- **"Generator ordering lives in code" is not a hard constraint this quarter.** It describes the generator driver, which isn't needed to prove an annotation replacement.

One disagreement sits under all of this and is judgment, not measurement: whether an explicit `TypeName` matters more than zero authoring. That values position decides between whole branches of the design.

## What one migrated service can show

The success factor is one annotation migrated across one service. That gives evidence for some criteria and none for others.

| A pilot shows | A pilot can't show |
|---|---|
| Fails-early at the migrated declarations; scoped generate cost; ergonomics on a real diff; incremental coexistence; the scoped loop; provider contract via byte-identical output | Change containment (needs the next new concern); full `make gen` cost; coverage across all consumers; authority provider-wide; generator ignorance across generators; generator ordering |

The right-column criteria need other evidence: historical walk-throughs of concerns added over time for change containment, the generate-cost measurements for the budget criterion, and separate experiments for the rest. The list-resource beachhead ([list-resource-experiment](../findings/list-resource-experiment.md)) is one such experiment and confirmed byte-identical registration for three resources.

## Uniformity across plugin frameworks is an assumption, not a criterion

Most options assume SDKv2 and Framework resources use the same authoring mechanism. No criterion requires that. The two frameworks already have different programming models, Framework has a designated `Metadata` method the provider routes through wrappers, and new resources are Framework. An option that treats them differently is penalized only if uniformity is required, and whether it is required is a judgment no measurement settles.
