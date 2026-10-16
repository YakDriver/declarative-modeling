# Magic Modules (MMv1)

## Summary

Google generates the `google` and `google-beta` Terraform providers from per-resource YAML. One spec file drives the resource, its tests, docs, and sweeper, for two provider variants (GA and beta). The useful thing to know: it has run this way for years at scale, and a typed loader plus schema validation did not stop the vocabulary from growing to about 90 fields on one struct.

## How it works

Resource facts are authored in external YAML at `mmv1/products/<product>/<Resource>.yaml`. A Go generator parses each file into an `api.Resource` struct and renders downstream code; `google` (TPG) and `google-beta` (TPGB) are generated repositories. The spec covers API contract and CRUD behavior, not only metadata: `base_url`, `self_link`, `create_url`/`create_verb`, `update_mask`, `delete_verb`, `async`, `timeouts`, `identity`, plus `parameters` and `properties`.

`api.Resource` carries about 90 YAML-serialized fields (commit de1637c, read 2026-10-16). The published reference documents about two dozen and says so: "This page documents commonly-used properties for resources. For a full list of available properties, see resource.go".

## What works

Centralized defaults, omitted on write. `setShallowDefaults()` fills `CreateVerb: POST`, `ReadVerb: GET`, `DeleteVerb: DELETE`, `UpdateVerb: PUT`. A custom `MarshalYAML` (commented "omit dynamic default values") strips any field still at its default, so authored files shrink as defaults land instead of growing.

Relational validation over one parsed model. `Resource.Validate()` accumulates a `[]error` and does cross-field checks, not only per-field ones: each `identity` entry must name a declared property ("missing property/parameter for identity %s"), verbs are checked against enums (`create_verb` one of POST/PUT/PATCH), and `is_list_of_ids: true` requires exactly one `identity` property.

A governed, one-way escape hatch. When a resource does not fit, two override levels exist. `custom_code` injects named template files into set points of the generated code (`encoder`, `decoder`, `pre_create`, `custom_update`, `custom_delete`, `custom_import`, `constants`, `extra_schema_entry`, and more). Beyond that a resource can go fully handwritten, under a documented rule: "New handwritten resources will only be accepted if implementing the resource in MMv1 would require entirely overriding two or more CRUD methods." Exiting is deliberately awkward: author in MMv1, generate, copy the generated files into `third_party/terraform`, modify, then delete the MMv1 config.

## What doesn't

Validation does not prevent vocabulary sprawl. The typed loader, the YAML schema, and `Validate()` coexist with about 90 fields and eleven separate opt-out keys: `exclude`, `exclude_resource`, `exclude_import`, `exclude_delete`, `exclude_read`, `exclude_sweeper`, `exclude_identity_generation`, `exclude_identity_from_identity_import`, `exclude_attribution_label`, `exclude_default_cdiff`, `exclude_tgc`. Validation catches malformed values, not unwarranted vocabulary.

Single-use keys land anyway, acknowledged in the struct:

```go
// Set to true for resources that wish to disable automatic generation of default provider
// value customdiff functions
// TODO rewrite: 1 instance used
ExcludeDefaultCdiff bool `yaml:"exclude_default_cdiff,omitempty"`
```

Two artifacts. Contributors author YAML and debug generated Go. The file you read is not the file you edit, and that cost grows with generated volume.

## Takeaways

- Schema validation buys correctness, not restraint. If you adopt an external spec, budget a separate mechanism to resist field-count growth, because a typed loader and a `Validate()` pass will not do it on their own. MMv1 is the existence proof.
- Steal the default handling. `setShallowDefaults` plus a `MarshalYAML` that omits defaults keeps authored files small as the vocabulary grows.
- Steal the relational validation. Checking the whole parsed model (identity names a real property, verbs against enums) catches a class of errors a per-field validator misses. Compare the unchecked string references flagged for [CloudFormation/awscc](cloudformation-awscc.md).
- Expect an escape hatch, and make exit awkward on purpose. Behavior does not fit declarative fields, so MMv1 needs both `custom_code` injection and a governed handwritten rule. Any generate-everything design needs the same, and the one-way, two-or-more-CRUD bar is a good model.
- An external file means two artifacts forever. If the debugged artifact matters more than the authored one, weigh typed host-language declarations (see [Upjet](upjet.md)) that keep both in one place.

## Sources

- [mmv1/api/resource.go](https://github.com/GoogleCloudPlatform/magic-modules/blob/main/mmv1/api/resource.go), commit de1637c (read 2026-10-16)
- [mmv1/api/resource/custom_code.go](https://github.com/GoogleCloudPlatform/magic-modules/blob/main/mmv1/api/resource/custom_code.go) (read 2026-10-16)
- [MMv1 resource reference](https://googlecloudplatform.github.io/magic-modules/reference/resource/) (read 2026-10-16)
- [Add a resource](https://googlecloudplatform.github.io/magic-modules/develop/add-resource/) (read 2026-10-16)
- [Magic Modules overview](https://googlecloudplatform.github.io/magic-modules/) (read 2026-10-16)
