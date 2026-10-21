# List resource shared-implementation experiment

Three hand-written list resources replaced by one shared implementation and typed declarations, published as [PR 50577](https://github.com/hashicorp/terraform-provider-aws/pull/50577). At three resources the provider is already shorter, and the flatten function signature is the main obstacle to converting the rest. Census at commit `15554cde8c1` (2026-10-20); experiment code at PR 50577 head `34ebfc0af5d` (2026-10-21).

## List resource population

| | Count |
|---|---:|
| `@SDKListResource` | 146 |
| `@FrameworkListResource` | 112 |
| `*_list.go` files (none generated) | 267 |
| Total lines in those files | 32,512 |

File size: min 9, median 112, mean 122, max 444 lines.

```console
git grep -c '@SDKListResource' 15554cde8c1 -- 'internal/service/*.go'
git ls-tree -r --name-only 15554cde8c1 internal/service | grep '_list\.go$'
```

List resources embed a shared base type, `framework.ListResourceWithSDKv2Resource`, and hand-write `List`. Nothing is generated.

## Shapes

The 142 SDKv2 list files that embed the base type divide by what `List` does. Counts are from [issue 50576](https://github.com/hashicorp/terraform-provider-aws/issues/50576), classified by reading the bodies at the census commit.

| Shape | Files | `List` body |
|---|---:|---|
| A | 43 | paginate, flatten whole objects straight from the page |
| B | 69 | paginate summaries, then `find*` each item |
| C | 25 | no flatten function, `rd.Set` inline |
| D | 5 | everything else |

Within a shape only the client accessor, input type, paginator, ID field, and flatten call differ.

186 functions in `internal/service` turn an SDK paginator into an `iter.Seq2`, all hand-written:

```console
git grep -h -A12 -E '^func [a-zA-Z]+\(.*\) iter\.Seq2\[' 15554cde8c1 -- 'internal/service/*.go' ':!*_test.go' \
  | awk '/^func /{if(f&&h)n++; f=1;h=0} /HasMorePages/{h=1} END{if(f&&h)n++; print n}'
```

## The declaration

Converted: `aws_cloudwatch_metric_alarm`, `aws_ecr_repository`, `aws_kms_alias`, all Shape A.

| Field | Content | Required |
|---|---|---|
| schema | the SDKv2 `resourceX()` function | yes |
| type argument | the AWS item type, as in `SDKListSpec[awstypes.Repository]` | yes |
| `Items` | closure binding client accessor, input type, and paginator | yes |
| `ID` | extracts the Terraform resource ID from one item | yes |
| `Flatten` | the resource's existing flatten function | yes |
| `DisplayName` | defaults to the ID | no |

Every field is a compile-checked Go symbol. None holds a string resolved by convention. The item type is written once per resource because Go doesn't infer type arguments in a composite literal, and a wrong one fails to compile against `Items` and `Flatten`.

`DisplayName` is not used by the three, but it earns its place across the population: in 96 of the 146 SDKv2 list files, the expression assigned to `result.DisplayName` differs from the one passed to `rd.SetId` (a text comparison, so approximate).

The `ID` extractor is deliberately not derived. `RepositoryName`, `AlarmName`, and `AliasName` suggest a convention, but a wrong derivation produces silently incorrect resource IDs, with no compile or generation error to catch it.

## Facts that dissolved rather than became fields

| Candidate | Outcome |
|---|---|
| display name | equals the ID in all three; defaults to the ID, so none of them sets the field |
| per-item error policy | ecr aborted the stream, cloudwatch and kms logged and continued; one default, no field |
| cleared-ID check | present only in kms, correct everywhere; moved into the shared loop |
| tflog field setup | identical in all three; moved into the shared loop |

All four were divergence, not configuration (see [divergence-is-not-configuration](../../concepts/divergence-is-not-configuration.md)).

## The flatten signature

`Flatten` takes `func(ctx, awsClient, item, d) error`, the signature `skaff/list/list_sdkv2.gtpl` generates, so a scaffolded resource binds unchanged. 16 of the 43 Shape A flatten functions already match it ([issue 50576](https://github.com/hashicorp/terraform-provider-aws/issues/50576)). The rest differ in return type and parameter order.

Across all 130 `*Flatten` functions in `internal/service` on 2026-10-08, return types were `error` 57, `diag.Diagnostics` 38, none 35. An attempt to normalize toward `diag.Diagnostics` failed on `return smarterr.NewError(fmt.Errorf(…))` inside `resourceMetricAlarmFlatten`.

Each flatten function has two call sites, `Read` and `List`. Changing one when its resource converts touches it once.

## Line accounting

| File | Before | After |
|---|---:|---:|
| `cloudwatch/metric_alarm_list.go` | 97 | 38 |
| `ecr/repository_list.go` | 91 | 35 |
| `kms/alias_list.go` | 100 | 35 |
| **Total** | **288** | **108** |

Shared code is 162 lines: `internal/framework/sdk_list_spec.go` (109) and `internal/iter/paginate.go` (53). Net at three resources is 18 lines shorter, about 60 saved per resource after that. Tests are not counted. The first spike (2026-10-08) converted the same three to 150 lines against 120 of shared code, 15 lines longer.

## Verification

At PR 50577 head:

- `_List_basic`, `_List_includeResource`, `_List_regionOverride`, and `_basic` pass for all three resources, 12 tests (output in the PR). `_basic` is included because each flatten is also called from `Read`.
- Registration is byte-identical after `make gen PKG=<service>` for ecr, kms, and cloudwatch.
- `internal/framework/sdk_list_spec_test.go` covers the branches acceptance tests can't reach: iterator error, flatten error, cleared ID, display name, and early stop.

## Not attempted

Shape B, the largest group. It sets attributes from the summary before a conditional detail fetch, so a shared version needs a second type parameter and a hook Shape A never exercises. `aws_sns_topic_policy` was an early candidate and is Shape B: it calls `findTopicAttributesWithValidAWSPrincipalsByARN` per item and derives its display name with `parseTopicNameFromARN`.
