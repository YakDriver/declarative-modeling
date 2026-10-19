# List resource shared-implementation experiment

Measures the provider's list resources, then an experiment that replaced three of them with one shared implementation and tested the result against AWS. Census measured 2026-10-08; experiment run 2026-10-08. The experiment's code is not yet published.

## List resource population

| | Count |
|---|---:|
| `@SDKListResource` | 144 |
| `@FrameworkListResource` | 103 |
| Total list resources | 247 |
| `*_list.go` files (none generated) | 256 |
| Total lines in those files | 31,320 |

Size distribution of the files: min 9, median 112, mean 122, max 444. Only 3 files are 60 lines or fewer; 156 are 61 to 120; 97 exceed 120. Of 72 services with list resources, 51 have between one and three; ec2 has 31, s3 and iam have 12 each.

Structural uniformity across the 256 files:

| Element present | Files |
|---|---:|
| a `List(ctx …)` method | 246 |
| `ListResultsStream` / `results.` | 243 |
| a paginator | 168 |
| `ListResourceConfigSchema` (Framework only) | 103 |
| AutoFlex (`fwflex.`) | 101 |
| any filtering | 27 |

A shared base implementation already exists: list resources embed a common type rather than being generated.

```go
// @SDKListResource("aws_ssm_parameter")
func newParameterResourceAsListResource() inttypes.ListResourceForSDK {
	l := parameterListResource{}
	l.SetResourceSchema(resourceParameter())
	return &l
}

type parameterListResource struct {
	framework.ListResourceWithSDKv2Resource
}
```

Generic behavior is embedded, per-resource specialization is written by hand, nothing is generated.

What varies per resource: the service client accessor, the AWS input type, the iterator/paginator function, which attributes are set on each result, whether `IncludeResource` triggers a secondary find, and AutoFlex versus manual mapping. The median body is 112 lines and 97 files exceed 120, so these are not thin wrappers.

## The experiment

Three list resources were expressed as typed Go declarations consumed by one generic implementation, then tested against AWS.

### Shape taxonomy

The 140 `*_list.go` files that embed `framework.ListResourceWithSDKv2Resource` divide into four shapes by what the `List` body does:

| Shape | Files | Body |
|---|---:|---|
| A. paginate, flatten each item directly | 53 | one paginated call returns whole objects |
| B. list identifiers, then describe each | 65 | paginated call plus a per-item `find*` |
| C. no flatten, manual `rd.Set` | 14 | attributes set inline |
| D. other | 8 | |

Shape A totals 6,685 lines, median 128. Shape B is the larger population and was not attempted. `aws_sns_topic_policy` was an initial candidate and is Shape B: it calls `findTopicAttributesWithValidAWSPrincipalsByARN` per item and derives its display name with `parseTopicNameFromARN`.

### What the declaration needs

Converted: `aws_cloudwatch_metric_alarm`, `aws_ecr_repository`, `aws_kms_alias`. Four fields were required, two optional. Each is a compile-checked Go symbol; no field holds a string resolved by convention.

| Field | Content | Required |
|---|---|---|
| `Items` | closure binding client accessor, input type, and paginator | yes |
| `ID` | extracts the Terraform resource ID from one item | yes |
| `Flatten` | the resource's existing flatten function | yes |
| schema | the SDKv2 `resourceX()` function | yes |
| `DisplayName` | defaults to `ID` | no |
| `OnItemError` | defaults to skip-and-log | no |

`Items` collapses four varying things (client accessor, AWS input type, paginator constructor, page field) into one binding, leaving the paginator itself as imperative Go.

### Facts that dissolved rather than became fields

Five candidates were eliminated, four by observing that the variation was divergence rather than configuration:

| Candidate | Outcome |
|---|---|
| AWS item type | inferred from `Items` by Go type inference; never authored |
| display name | equals the ID in all three; defaulted |
| per-item error policy | ecr aborted the stream, cloudwatch and kms logged and continued; one default chosen |
| cleared-ID check | present only in kms, correct everywhere; moved into the shared loop |
| tflog field setup | identical in all three; moved into the shared loop |

The ID extractor was deliberately not derived. `RepositoryName`, `AlarmName`, and `AliasName` suggest a convention, but a wrong derivation produces silently incorrect resource IDs, with no compile or generation error available to catch it.

### The flatten-contract obstacle

`*Flatten` functions have no single signature. Across 130 of them in `internal/service`:

| Return type | Count |
|---|---:|
| `error` | 57 |
| `diag.Diagnostics` | 38 |
| none | 35 |

The AWS item parameter is a pointer in 112 and a value in 18.

One spec field cannot accept three contracts. Normalizing to `error` was chosen because it is the plurality and composes with smarterr, the provider's stated direction. An attempt to normalize toward `diag.Diagnostics` failed on `return smarterr.NewError(fmt.Errorf(…))` inside `resourceMetricAlarmFlatten`. Cost per resource, each having exactly two call sites:

| Resource | Starting contract | Lines changed |
|---|---|---:|
| `aws_cloudwatch_metric_alarm` | `error` | 0 |
| `aws_ecr_repository` | none | 2 |
| `aws_kms_alias` | `diag.Diagnostics` | 3 |

Roughly 95 of the 130 are not yet on the `error` contract.

### Line accounting

| File | Before | After |
|---|---:|---:|
| `cloudwatch/metric_alarm_list.go` | 97 | 52 |
| `ecr/repository_list.go` | 91 | 49 |
| `kms/alias_list.go` | 100 | 49 |
| **Total** | **288** | **150** |

The shared implementation (`internal/framework/sdk_list_spec.go`) is 120 lines. Net across three resources is +15; break-even falls near the fourth, with roughly 45 lines saved per resource after that. Extrapolating Shape A gives order 6,000 lines, conditional on the flatten normalization above. Of the 49-line converted file, 12 lines are the declaration, 18 the paginator helper, 12 imports, 4 header.

### Verification

22 acceptance test executions across 6 runs, 11 distinct tests, zero failures: `_List_basic`, `_List_includeResource`, and `_List_regionOverride` for all three resources, plus `_basic` for ecr and kms because their flatten functions are also called from `Read`.

`_List_regionOverride` was identified in advance as the likeliest failure: the declaration resolves the service client inside the stream closure, whereas the original resolved it at `List` entry. It passed for all three.

Registration is byte-identical after `make gen` for all three services, because the factory function names were preserved and only their bodies replaced. Provider-wide `go build ./...`, the four affected packages' unit tests, `make quick-fix`, and `make copyright` all pass.

Signals that did not appear during the conversion: no per-resource custom-code knobs, no string-named function references, no generator-specific flags. The declaration stayed at four required fields across all three resources. This was tested only within Shape A; Shape B was not attempted.
