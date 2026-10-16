# Pulumi package schema and the Terraform bridge

## Summary

Pulumi describes every provider with one package schema (`schema.json`) that drives SDK code generation for each supported language. `pulumi-aws` is not authored from an independent schema: it is produced by `pulumi-terraform-bridge`, which generates both the schema and a running RPC shim from the Terraform AWS provider plus a typed-Go mapping.

## How it works

Two layers sit on top of each other.

The package schema is an external JSON document of resources, functions, types, and a `language` map. It "drives code generation for SDKs in each supported Pulumi language, as well as generation of language-agnostic package documentation," and "can be manually authored (for component packages) or generated from some other source." `pulumi schema check` validates it against a metaschema. Cross-references are `$ref` URIs resolved against a document and type token, for example `/aws/v7.44.0/schema.json#/resources/aws:apigateway%2FrestApi:RestApi`, a checked reference rather than a free string.

For a bridged provider the schema is generated, not hand-written. The bridge "code-generate[s] packages by dynamic inspection of a Terraform Provider's schema" at build time (the `tfgen` command), and at runtime "connects the Pulumi engine to a given Terraform Provider using Pulumi's RPC interfaces," reusing the same schema for validation and diffs. Authoring happens in typed Go. `Provider()` returns a `tfbridge.ProviderInfo` whose `Resources` and `DataSources` maps carry per-resource overrides, and token derivation is a call:

```go
prov := tfbridge.ProviderInfo{
	P:         p,
	Name:      "aws",
	GitHubOrg: "hashicorp",
	Resources: resourceOverrides(p),
	DataSources: dataSourceOverrides(),
}
prov.Resources["aws_s3_bucket"].Fields["bucket"].CSharpName = "BucketName"
prov.MustComputeTokens(awsTokenStrategy(&prov))
prov.MustApplyAutoAliases()
```

## What works

One schema, many language surfaces: nodejs, python, go, csharp, java, yaml. This is the clearest case where a serialized external spec earns its keep, because the consumers are genuinely heterogeneous.

Each generator owns its `language` extension. "The shape of that object is decided by that language's SDK code generator rather than by the schema itself." The core model stays language-neutral, and a new consumer adds its own slice (an NPM package name, a Go import path) without touching the shared schema.

Cross-references are checked through `$ref` against a resolved token, the same idea as CloudFormation's JSON pointers ([cloudformation-awscc](cloudformation-awscc.md)).

Derive first, author the residue. The bridge generates what it can from the Terraform schema, so the mapping only carries what cannot be derived: a token strategy, renames like `CSharpName = "BucketName"`, aliases, autonaming. Because the residue is typed Go referencing upstream symbols, a wrong reference is a build error, not a silent string miss.

Roles are split, not merged. The generator emits SDKs and docs from the schema; a shared RPC runtime does validation and diff off the same Terraform schema. Both a generator and a shared runtime, not one.

## What doesn't

The bridge inherits Terraform's semantics. The schema is a projection of the Terraform provider, not an authority over it. Resource behavior stays in the Terraform provider ([terraform-provider-aws-annotations](terraform-provider-aws-annotations.md)); the schema describes shape, and the shim defers lifecycle to Terraform. Whatever the upstream schema cannot express, the Pulumi schema cannot either.

The source of truth is another team's repo: `GitHubOrg: "hashicorp"`. Bridged output tracks upstream, quirks included. The mapping file carries backward-compat shims, such as re-adding a removed `aws_ecr_credentials` data source as a proxy to `aws_ecr_authorization_token`.

Coverage gaps can go quiet. `tfgen` can be told to skip an unmapped resource with only a warning (`PULUMI_SKIP_MISSING_MAPPING_ERROR`), so a missing mapping does not fail the build unless the strict default is kept.

## Takeaways

A serialized external spec is justified by heterogeneous consumers. Pulumi's six language targets are the warrant; a single host language is not ([smithy](smithy.md)). If your only consumer is one Go toolchain, a serialized format is cost without the payoff.

Keep the core model language-neutral and let each consumer own an extension slice. The `language` map is the seam: generators add fields there without changing the shared schema. An intermediate model with a stable core and per-consumer extensions is the reusable shape ([tfplugingen](tfplugingen.md)).

Make references checked. A `$ref` into a schema token, or a typed Go reference to an upstream symbol, fails at build time when the target is wrong. A free string does not.

Bridging buys breadth fast and inherits the upstream's semantics and limits with it. A schema generated over someone else's provider is a projection. Decide deliberately whether you want a projection or an authority, because you cannot add expressiveness the source lacks.

Derive the bulk, author only the residue, and author it in typed code so its references compile.

## Sources

- [Pulumi package schema](https://www.pulumi.com/docs/iac/guides/building-extending/packages/schema/), read 2026-10-16.
- [pulumi-terraform-bridge README](https://github.com/pulumi/pulumi-terraform-bridge/blob/master/README.md), read 2026-10-16.
- [pulumi-aws `provider/resources.go`](https://github.com/pulumi/pulumi-aws/blob/ca34048d18e00d42c77ea43fa758568b3051fa0d/provider/resources.go), read 2026-10-16.
- [pulumi-aws `schema.json`](https://github.com/pulumi/pulumi-aws/blob/master/provider/cmd/pulumi-resource-aws/schema.json) (bridged provider package), read 2026-10-16.
