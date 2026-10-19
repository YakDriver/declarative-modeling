# Registration entries

What the provider's resource registration costs, how much of it is derivable, and how it is keyed. Measured on the terraform-provider-aws repository 2026-10-01, from all `service_package_gen.go` files, excluding `_test.go` and generated files unless noted.

## Size

- 2,679 entries, 20,866 lines (average 7.8 per entry).
- 1,123 entries (42%) have no `Tags`, `Identity`, or `Import`: one annotation line becomes about 6 generated lines.
- Field presence: `Factory`, `TypeName`, `Name`, `Region` 2,679 each; `Tags` 1,192; `Identity` 785; `Import` 536.
- 3,953 lines are nested deeper than a top-level field, mostly identity and import constructors.
- `Region`: `ResourceRegionDefault()` 2,363 (88%), `ResourceRegionDisabled()` 303, `ResourceRegionNoPartitionValidation()` 9, `ResourceRegionDeprecatedOverride()` 4.
- `Tags`: `ResourceTagsAttribute` 1,004, `ResourceTagsInline` 136, `ResourceTagsTypeAndAttribute` 52.
- Registrations per service (274 services): median 5, 90th percentile 22; largest sagemaker 43, s3 50, rds 52, iam 67, ec2 288.
- 552 type names are registered more than once, typically a resource and a data source sharing a name, plus aliases such as `aws_alb` / `aws_lb`.

## Deriving TypeName and Name

Rule tested: strip the factory's role prefix or suffix (`resource`, `dataSource`, `new…Resource`), snake-case the rest, and prepend the service's `resource_prefix` (`actual` or `correct`) from `names_data.hcl`.

| Field | Derivable | Notes |
|---|---:|---|
| `TypeName`, exact with prefix | 2,260 / 2,679 (84.4%) | 419 misses |
| `TypeName`, suffix only | ~96% | prefix still needed |
| `Name` from type-name suffix (title case, case-insensitive) | 2,249 / 2,679 (84%) | |
| `Name` from factory name | ~91% | |

Misses by service: ec2 183, elbv2 29, logs 27, rds 27, cognitoidp 20, elb 10, meta 8, odb 7.

17 `resource_prefix.actual` values are regexes, not strings. elbv2's is `aws_a?lb(\b|_listener|_target_group|s|_trust_store)` (`correct` = `aws_elbv2_`). A derivation rule cannot prepend these. Services with regex prefixes: ec2, elbv2, logs (`aws_cloudwatch_(log_|query_)`), rds (`aws_(db_|rds_)`), cognitoidp, elb, meta. Those are 7 of the 8 services with the most misses.

Miss categories:

- Legacy top-level names, mostly ec2: `aws_vpc`, `aws_subnet`, `aws_ami`.
- Aliases and short names: `newLoadBalancerResource` becomes `aws_lb`, plus `aws_alb`.
- Acronym tokenization in the rule: `IPSet` becomes `ipset`; also `VoIP`, `FSx`, `MacSec`.
- Irregular word joins: `SpotDataFeedSubscription` becomes `spot_datafeed_subscription`; `LifeCycle` becomes `lifecycle`.
- Friendly names that differ: `dataSourceZone` is "Hosted Zone", `resourceAddon` is "Add-On", `resourceDefaultRouteTable` is "Route Table".

A derived `Name` that differs from today's value moves checked-in `testdata/{Name}/` fixture directories and breaks tests that reference the old path, because `Name` is the fixture-directory path component at generation time (see [provider-contract.md](provider-contract.md)). This affects the ~9 to 16% of names that do not derive.

## Finding factories without annotations

- 1,770 non-test functions have the shape `func x() *schema.Resource`; 1,754 SDK resources and data sources are registered.
- 31 of those functions are not registered factories: schema versions and helpers such as `resourceClusterV0`, `launchTemplateSchemaV0`, `flowLogSchemaV0`, `networkACLRuleNestedBlock`, `resourceInstanceResourceV1`.
- 680 functions match a crude Framework factory signature (`func newX(context.Context) (resource.…`); 783 Framework registrations exist. The signature pattern needs refining to close the gap.

## Keys, identifiers, and ordering

- Type names are not unique across kinds. Distinct type names: 1,728 managed resources, 683 data sources; 395 are registered as both (`aws_acm_certificate`, `aws_acmpca_certificate`). Uniqueness is per (kind, type name), not across kinds.
- Three-state keys. `common.TriBoolean` (`internal/generate/common/resource_identity.go:17-22`) has `Unset`, `True`, `False`. It types three values: tag-test generation (`tagsTest`), `wrappedImport`, and `isARNFormatGlobal`. Explicit `false` is written for other keys too, whether or not their parsers distinguish it from absent: `tagsTest` 215, `generator` 129, `identityTest` 17, `identityRegionOverrideTest` 17, `overrideEnabled` 16, `validateOverrideInPartition` 9, `hasExistsFunction` 8.
- Source filename is a generator input. `tagstests/main.go:118-124` derives the generated test filename from the Go source filename, trimming a trailing `_` (for files like `ec2/vpc_.go`). The fixture template path is `testdata/tmpl/{sourceName}_basic.gtpl` (`:179`, `:230`).
- Type prefix is not the Go package. `aws_vpc` is implemented in `internal/service/ec2/vpc_.go`; no `internal/service/vpc` exists.
- Identity attribute order is used at runtime. `Identity.Attributes` is a slice iterated in order by importers and interceptors (`framework/importer/parameterized.go:71,101`, `sdkv2/identity_interceptor.go:50,85,117`); `sdkv2/importer/inherent_regional_id.go:16` reads `Attributes[0]`.
