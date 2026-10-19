# Terraform AWS provider annotations

## Summary

HashiCorp's AWS provider, about 2,700 resources and data sources, puts resource metadata in Go comment markers above the factory function. Code generators parse them into a per-service `service_package_gen.go` and into generated tests. It is comment markers feeding generators, the same family as [controller-gen](controller-gen.md), and it has reproduced the same failure modes.

## How it works

A marker sits on the factory, and generators read it:

```go
// @FrameworkResource("aws_timestreaminfluxdb_db_instance", name="DB Instance")
// @Tags(identifierAttribute="arn")
// @IdentityAttribute("id")
// @Testing(existsType="...;timestreaminfluxdb.GetDbInstanceOutput")
func newDBInstanceResource(_ context.Context) (resource.ResourceWithConfigure, error) {
```

Three generators each run their own AST walk over the same comments: `servicepackage` (registration, tags, identity), `tagstests`, and `identitytests`. `servicepackage` emits a registration struct (`Factory`, `TypeName`, `Name`, `Region`, `Tags`, `Identity`, `Import`) into the service's `service_package_gen.go`. At startup the provider reads those fields to wire interceptors, importers, and identity. For Framework resources the wrapper's `Metadata` returns the registered `TypeName` and never calls the inner resource, so registration is the only source of a Framework type name.

The surface is 7,025 marker lines in 2,670 files, 25 marker kinds, not counting tests or generated files ([inventory](../terraform-provider-aws/findings/surface.md), 2026-10-01).

## What works

The markers solved concrete problems, documented in issue [#26626](https://github.com/hashicorp/terraform-provider-aws/issues/26626) and PR [#28933](https://github.com/hashicorp/terraform-provider-aws/pull/28933):

- A single `provider.go` listing every resource "becomes unwieldy (and a source of merge conflicts) when there are a few thousand" (#26626). Self-registration removed that file.
- #28933 replaced an `init()` prototype because the HashiCorp Go style guide forbids `init()` registries. The marker sits next to the factory, so adding a resource touches one file.
- Registration grows only with the resource count, and `make gen PKG=xyz` regenerates one service without a provider-wide run.

## What doesn't

The marker is a string the compiler never sees, so mistakes are silent. `elasticache/reserved_cache_node.go:37` reads `@Testing(tagsTests=false)`; the key is `tagsTest`, so nothing reads it. It has been wrong since 2023 and is still present (verified 2026-10-16). Unknown keys and lines that miss the marker regex are both dropped without warning.

Strings restate what Go already holds. `@Testing(existsType=...)` writes the resource's Go type as a string 492 times, the single largest key ([`@Testing` keys](../terraform-provider-aws/findings/testing-keys.md)), duplicating the type a finder already returns.

Vocabulary sprawls, and the format does not stop it. `@Testing` carries 54 keys, 13 used exactly once ([`@Testing` keys](../terraform-provider-aws/findings/testing-keys.md)). The surface grew 2.75x between April 2024 and October 2026, about half of it `@Testing` ([history](../terraform-provider-aws/findings/history.md)). One comment language now does four jobs with different lifetimes: four `@Testing` keys cross into the production generator path, and two test-only keys sit on production markers ([silent failures](../terraform-provider-aws/findings/silent-failures.md)). None of the 3,063 parsing lines has a test ([generators](../terraform-provider-aws/findings/generators.md)).

The merged [principles doc](https://github.com/hashicorp/terraform-provider-aws/blob/main/docs/design-decisions/declarative-resource-modeling-principles.md) names the fixes: prefer typed Go whose references the compiler checks, bind behavior rather than encode it as strings, and make a new field pay rent before it is added.

An experiment run 2026-10-08 (not yet published) tested the alternative on list resources, which already embed a shared base (`framework.ListResourceWithSDKv2Resource`, 138 files on 2026-10-16) rather than being generated. Three list resources were rewritten as typed Go declarations feeding one shared implementation. Four fields were required, each a compile-checked Go symbol, no string resolved by convention. Five candidate facts dissolved into the shared loop instead of becoming configuration. Registration stayed byte-identical and all acceptance tests passed. The obstacle was not the metadata: the shared implementation needed one flatten contract, and the 130 flatten functions return three different types (`error`, `diag.Diagnostics`, none). Normalizing that, not authoring the declaration, was the real cost.

## Takeaways

- Comment markers buy co-location and solve registration cheaply, but every value is an unchecked string. Budget for a separate linter from day one, because the format is not a checker and silent typos survive for years.
- A schema or parser catches malformed values, not unneeded ones. Sprawl comes from adding one defensible key at a time. Require each new field to name its authority, consumers, validation, and failure mode, or it accretes.
- When a fact names a Go symbol (a type, a function, a factory), author it as typed Go so the compiler checks it and renames carry. Reserve a serialized format for bulk data that names no symbols and crosses a process boundary.
- Typed declarations feeding a shared runtime let per-resource facts dissolve into the shared implementation rather than persist as metadata. The hard part is normalizing one contract across existing code, so the win scales only after that normalization. See [Upjet](upjet.md) for the same shape at scale, and [tfplugingen](tfplugingen.md) for where an external spec stops at schema.

## Sources

- [terraform-provider-aws issue #26626](https://github.com/hashicorp/terraform-provider-aws/issues/26626), read 2026-10-16
- [terraform-provider-aws issue #50242](https://github.com/hashicorp/terraform-provider-aws/issues/50242), read 2026-10-16
- [terraform-provider-aws PR #28933](https://github.com/hashicorp/terraform-provider-aws/pull/28933), read 2026-10-16
- [declarative-resource-modeling-principles.md](https://github.com/hashicorp/terraform-provider-aws/blob/main/docs/design-decisions/declarative-resource-modeling-principles.md), read 2026-10-16
- [Provider findings](../terraform-provider-aws/findings/README.md), measured 2026-10-01 to 2026-10-08 on the provider's `main` branch
