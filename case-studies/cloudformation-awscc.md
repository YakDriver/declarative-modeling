# CloudFormation resource provider definition schema (terraform-provider-awscc)

## Summary

AWS's CloudFormation CLI defines each resource type as a per-type JSON Schema document, validated by one meta-schema: the Resource Provider Definition Schema. HashiCorp's `terraform-provider-awscc` is generated wholesale from those schemas, so a spec-driven AWS Terraform provider already ships. The most useful thing to copy is how it points at schema locations: JSON pointers resolved against the declared schema, not free strings.

## How it works

Facts about a resource are authored in an external JSON file per type and consumed by a generator. Like [Magic Modules](magic-modules.md), the authored artifact is not the code you debug.

The meta-schema declares, per type:

- `primaryIdentifier`, `additionalIdentifiers`: lists of JSON pointers to identifying properties.
- `createOnlyProperties`, `readOnlyProperties`, `writeOnlyProperties`, `conditionalCreateOnlyProperties`, `deprecatedProperties`: lists of JSON pointers.
- `tagging`: an object with `taggable`, `tagOnCreate`, `tagUpdatable`, `cloudFormationSystemTags`, and `tagProperty` (a JSON pointer, default `/properties/Tags`).
- `handlers` for `create`, `read`, `update`, `delete`, `list`, each carrying IAM `permissions` and a `timeoutInMinutes`.

Two things stand out for a metadata designer. References point into the schema: `tagProperty` defaults to `/properties/Tags`, so a validator can confirm the target property exists, and the same holds for every `*Properties` pointer list. And the spec carries operational metadata most IDLs omit: per-handler IAM permissions ("You must specify at least one permission for each handler") and timeouts (`timeoutInMinutes`, default 120, minimum 2, maximum 2160).

## What works

- Checked references. A JSON pointer resolved against the declared schema is a structurally verifiable link, unlike a bare string naming an attribute. This is the single idea most worth stealing (compare traits in [Smithy](smithy.md)).
- One spec drives multiple artifacts. awscc generates the managed resource plus singular and plural data sources from the same schema file.
- Breadth is cheap. Any type AWS publishes a schema for can be generated without hand-writing CRUD.

## What doesn't

The upstream spec could not express the Terraform contract, and the generator's workarounds are the lesson.

CloudFormation does not expose property defaults consistently, so awscc makes every optional, non-read-only property Computed. From the generator (`internal/tools/bigdiffer/codegen/emitter.go`):

```go
if !required && !readOnly {
    optional = true
}
// All Optional attributes are also Computed.
if optional && !computed {
    computed = true
}
```

Making omitted values Computed suppresses spurious diffs but means Terraform no longer detects drift on anything the user leaves unset. That is a semantic loss forced by a gap in the source spec, not a bug.

Some resources cannot be generated at all and are suppressed in `all_schemas.hcl` (47 `suppress_resource_generation` entries, alongside 35 frozen schemas, at commit `d4a01a6`). The irony for a metadata designer: the spec's own references are checked JSON pointers, but awscc records *why* a resource is suppressed in a free-form comment above the block, "a convention, not a schema field, so it is invisible to any tooling." For example:

```hcl
# Suppression Reason:
# Recursive Attribute Definitions https://github.com/hashicorp/terraform-provider-awscc/issues/95
suppress_resource_generation = true
```

The checked-reference discipline stopped where the spec stopped, and the escape hatch fell back to unchecked strings.

Breadth is also not fitness. I think the hand-written provider is still the one most people reach for, so coverage alone didn't settle which provider wins.

## Takeaways

- Make references point into the model. If a field names a schema location (a tag property, an identifier, a read-only path), encode it as a resolvable pointer so a validator can prove the target exists. Terraform-provider-aws's `@Tags(identifierAttribute="arn")` is the unchecked-string version of the same fact.
- A spec carries only what its authority exposes. CloudFormation could not express defaults, so the generated provider lost drift detection on omitted values. Before choosing an external spec, confirm the source can express every semantic the consumer needs; where it can't, expect a lossy default like blanket Computed.
- Operational metadata (per-handler permissions, timeouts) is worth declaring when the host can declare it. CloudFormation does; the Plugin Framework providers have no analog.
- Watch the escape hatch. The moment generation can't handle a type you need somewhere to say so, and if that somewhere is a comment, it is invisible to the validation you built for everything else.

## Sources

- [Resource type schema](https://docs.aws.amazon.com/cloudformation-cli/latest/userguide/resource-type-schema.html), CloudFormation CLI User Guide (tagging, tagProperty, handlers permissions and timeouts, pointer lists), read 2026-10-16.
- [Resource Provider Definition Schema meta-schema](https://github.com/aws-cloudformation/cloudformation-cli/blob/master/src/rpdk/core/data/schema/provider.definition.schema.v1.json), read 2026-10-16.
- [`internal/tools/bigdiffer/codegen/emitter.go`](https://github.com/hashicorp/terraform-provider-awscc/blob/d4a01a652e8799c3c96cb350e6eca37289a642e4/internal/tools/bigdiffer/codegen/emitter.go) (optional becomes Computed), read 2026-10-16.
- [`internal/provider/generators/allschemas/allschemas.go`](https://github.com/hashicorp/terraform-provider-awscc/blob/d4a01a652e8799c3c96cb350e6eca37289a642e4/internal/provider/generators/allschemas/allschemas.go) (suppression fields), read 2026-10-16.
- [`contributing/docs/suppressed-and-frozen.md`](https://github.com/hashicorp/terraform-provider-awscc/blob/d4a01a652e8799c3c96cb350e6eca37289a642e4/contributing/docs/suppressed-and-frozen.md) (suppression counts, reason-as-comment, example), read 2026-10-16.
