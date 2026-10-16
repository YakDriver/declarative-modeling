# A declarative system is either spec-authoritative or code-authoritative

A system that models resources declaratively is one of two things. Either the declaration is the source of truth and the code is generated from it, or the code is the source of truth and the declaration describes it. The split is about authority, not file format.

## What each architecture must carry

When the spec is the contract, it has to carry enough to produce behavior. [Magic Modules](../case-studies/magic-modules.md) generates Google's Terraform providers from per-resource YAML, and that YAML names `base_url`, `create_verb`, `update_mask`, `async`, and about ninety fields. [CloudFormation's resource schemas](../case-studies/cloudformation-awscc.md) that generate `terraform-provider-awscc` carry per-handler IAM permissions and timeouts. The code is output, so drift between spec and code is impossible.

When the code is the truth, the declaration only needs what the code and generators cannot recover. [Upjet](../case-studies/upjet.md) derives schema, controller logic, and sensitive-field handling from an existing Terraform provider and authors only the residue as typed Go; [controller-gen](../case-studies/controller-gen.md) keeps resource shape in Go structs and attaches metadata as markers. Drift is possible here: a marker can be stale or wrong, and nothing regenerates it.

## Hybrid surface is normal; hybrid authority is the defect

Every mature spec-driven system is a hybrid. Magic Modules supports handwritten resources and injects Go through `custom_code`, and a CloudFormation schema describes shape while a handler implements behavior.

The defect is hybrid authority: the same fact owned in two places with no arbiter. A healthy split gives each fact one owner; the unhealthy one copies it across spec, implementation, and test and leans on a convention to keep them aligned. See [divergence is not configuration](divergence-is-not-configuration.md).

## Semantic facts and implementation facts

A fact either describes the resource or describes the code that happens to implement it today. The test is whether it survives a rewrite of the code. The read operation `GetDbInstance`, the resource's type name, whether it is taggable: these hold no matter how the code is organized. A Go output type, a constructor's name, a finder's name: these change when the code changes.

Only resource facts belong in a model. An implementation fact belongs there only as a checked link, never as a copied string. Storing a Go type name in a spec relocates an implementation detail into another language; naming the read operation describes the resource, and the Go type follows. So the starting question for any model is not "which fields can move into it?" but "which facts describe the resource independently of how we implement it today?" See [derive before authoring](derive-before-authoring.md) and [what must survive](what-must-survive.md).

## What each architecture costs

Spec-as-contract:

- Schema validation does not stop vocabulary from growing. Magic Modules has a typed loader, a schema, and a `Validate()` pass, and still carries about ninety fields, eleven `exclude_*` opt-out keys, and a single-use field marked `// TODO rewrite: 1 instance used`. Validation catches malformed values, not unwarranted vocabulary. See [vocabulary governance](vocabulary-governance.md).
- The authored artifact stops being the one you debug: contributors edit YAML and read generated Go.
- Misspellings go silent unless someone builds the checker. controller-gen ignores a marker written `enum` when it expects `Enum`.
- An external spec must express behavior or stop short. awscc could not express the Terraform contract and fell back to marking every optional property Computed, losing drift detection on unset values.
- Compile-checked references are lost and must be rebuilt. CloudFormation invented JSON pointers to recover a fraction of what a Go reference gives for free.

Metadata-on-code:

- Stringly edges remain wherever a declaration must name a schema field. Upjet's `OmittedFields` is `[]string`; a checked reference would need generated field constants, which is extra machinery.
- Generators must interpret Go literals or load whole packages, heavier than parsing a data file.
- Shared implementations concentrate behavior away from the resource: better for changing it, worse for explaining one in isolation.
- A typed struct can still grow into an oversized vocabulary one defensible field at a time; host-language values are no guard against sprawl.

I think neither side is free of sprawl: the same patterns show up in a schema-validated spec, so changing the form of the surface is not by itself evidence it will stay small.
