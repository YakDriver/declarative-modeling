# Annotation inventory

Counts the annotation markers in the Terraform AWS provider: how many, what job each does, how they spread across files, and which combinations recur. Measured on this repository 2026-10-01, repeated combinations 2026-10-06, excluding `_test.go` and generated files unless noted.

Top line: 7,025 annotation lines across 2,670 files in 252 of 274 service packages, 25 distinct top-level markers. Counted with `rg '^//\s*@<Marker>' internal/service --type go`.

By job: registration 2,679, `@Testing` 2,275, `@Tags` 1,051, identity/import 894, versioning 83, region 43. `@Testing` carries 54 keys, 13 of them used once (see [testing-keys.md](testing-keys.md)).

## Every marker

| Count | Marker | Job |
|---:|---|---|
| 2,275 | `@Testing` | test generation |
| 1,240 | `@SDKResource` | registration |
| 1,051 | `@Tags` | tagging |
| 514 | `@SDKDataSource` | registration |
| 488 | `@FrameworkResource` | registration |
| 479 | `@IdentityAttribute` | identity |
| 178 | `@ArnIdentity` | identity |
| 169 | `@FrameworkDataSource` | registration |
| 142 | `@SDKListResource` | registration |
| 115 | `@ImportIDHandler` | import |
| 103 | `@FrameworkListResource` | registration |
| 70 | `@V60SDKv2Fix` | versioning/compat |
| 43 | `@Region` | region |
| 31 | `@CustomImport` | import |
| 30 | `@SingletonIdentity` | identity |
| 24 | `@ArnFormat` | identity/format |
| 13 | `@IdAttrFormat` | identity/format |
| 12 | `@IdentityVersion` | versioning/compat |
| 12 | `@Action` | registration |
| 11 | `@EphemeralResource` | registration |
| 9 | `@MutableIdentity` | identity |
| 7 | `@NoImport` | import |
| 4 | `@WrappedImport` | import |
| 4 | `@CustomInherentRegionIdentity` | identity |
| 1 | `@IdentityFix` | versioning/compat |

Some `@Testing` keys feed identity validation, not only test generation (see [testing-keys.md](testing-keys.md)).

## By job

| Job | Lines |
|---|---:|
| Registration | 2,679 |
| Test generation (`@Testing`) | 2,275 |
| Tagging (`@Tags`) | 1,051 |
| Identity / import | 894 |
| Versioning / compat | 83 |
| Region | 43 |

Registration groups 8 markers (`@SDKResource`, `@FrameworkResource`, the matching data-source and list markers, `@EphemeralResource`, `@Action`). Identity/import groups 11. Non-`@Testing` total: 4,750 lines.

## Distribution

Annotations per file:

| Per file | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Files | 1,326 | 463 | 234 | 113 | 137 | 141 | 97 | 79 | 46 | 18 | 9 | 7 |

Maximum is 12, reached by `route53/record.go`, `redshift/namespace_registration.go`, `organizations/delegated_administrator.go`, `ecs/task_definition.go`, `datazone/policy_grant.go`, and two others.

Top services by annotation lines: ec2 742, iam 162, bedrockagentcore 154, s3 136, rds 135, apigateway 132, logs 131, securityhub 128, sagemaker 119, eks 100.

## Keyword arguments of non-`@Testing` markers

`@Testing` keys are covered in [testing-keys.md](testing-keys.md). The other markers:

| Marker | Keys (count) |
|---|---|
| `@SDKResource` | `name` 1,240 |
| `@FrameworkResource` | `name` 488 |
| `@Tags` | `identifierAttribute` 916, `resourceType` 39 |
| `@IdentityAttribute` | `optional` 21, `identityDuplicateAttributes` 9, `testNotNull` 6, `resourceAttributeName` 5, `valueType` 4 |
| `@ArnIdentity` | `identityDuplicateAttributes` 25, `duplicatesIdAttr` 1 |
| `@SingletonIdentity` | `identityDuplicateAttributes` 13 |
| `@Region` | `overrideEnabled` 16, `global` 14, `validateOverrideInPartition` 9, `overrideDeprecated` 4 |
| `@ImportIDHandler` | `setIDAttribute` 8 |
| `@ArnFormat` | `attribute` 7, `global` 5 |
| `@IdentityVersion` | `sdkV2IdentityUpgraders` 2 |
| `@V60SDKv2Fix` | `v60RefreshError` 1 |

## Repeated combinations and default candidates

Measured 2026-10-06. Method: runs of annotation comment lines immediately preceding a `func` declaration, in `internal/service`, excluding `_test.go` and `*_gen.go`. 2,668 blocks (slightly below the 2,679 registrations because one block can register several type names). 1,320 blocks, 49.5%, carry a single annotation.

Two levels of signature give opposite answers:

| Signature | Distinct | Occur once | Top 5 | Top 10 | Top 20 |
|---|---:|---:|---:|---:|---:|
| Marker set only | 89 | 32 (36%) | 51.6% | 71.3% | 88.1% |
| Markers + keys + short values | 651 | 536 (82%) | 49.2% | 62.4% | 68.7% |

Most frequent full combinations:

| Blocks | Share | Combination |
|---:|---:|---|
| 451 | 16.9% | `@SDKResource` only |
| 337 | 12.6% | `@SDKDataSource` only |
| 241 | 9.0% | `@SDKResource` + `@Tags(identifierAttribute="arn")` |
| 143 | 5.4% | `@SDKListResource` only |
| 141 | 5.3% | `@FrameworkResource` only |
| 121 | 4.5% | `@FrameworkDataSource` only |
| 103 | 3.9% | `@FrameworkListResource` only |

Individual facts recur, their conjunctions do not. The three largest entries, 40% of all blocks, are bare registrations and registration-plus-tags. For a worked combination (Framework resource with `id` identity, `arn` tags identifier, `@Testing` carrying `preCheck` and `hasNoPreExistingResource`), each component is common (`identifierAttribute="arn"` 659, `preCheck` 129, `hasNoPreExistingResource` 128, `IdentityAttribute("id")` 94) but all four appear together only 7 times.

Where one value dominates a key, that value is a candidate for being implicit rather than authored. Of 1,053 `@Tags` lines:

| Value | Lines | Share |
|---|---:|---:|
| `identifierAttribute="arn"` | 659 | 62.6% |
| `identifierAttribute="id"` | 153 | 14.5% |
| No arguments at all | 135 | 12.8% |
| Other (`name`, `rule_arn`, `job_arn`, …) | long tail, ≤7 each | |

`@IdentityAttribute` has no comparable dominant value: `id` 94, `name` 80, `bucket` 16, then a tail. For comparison, 88% of registrations use default region behavior and none of them author it (see [registration.md](registration.md)).
