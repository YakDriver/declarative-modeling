# Deriving existsType

Whether the `@Testing existsType` key can be derived from existing code instead of authored. Measured 2026-10-06 (derivation routes) and 2026-10-08 (Exists helpers).

`existsType` holds the resource's Go type as a string, for example `"github.com/aws/aws-sdk-go-v2/service/timestreaminfluxdb;timestreaminfluxdb.GetDbInstanceOutput"`. It is the single largest key in the annotation surface (see [surface.md](surface.md)).

Measured 2026-10-06 over all 494 `existsType` occurrences (492 two days earlier; two counting methods, any `existsType=` in a non-test non-generated file and only well-formed single-line `@Testing` annotations, agree exactly at 494). Two candidate sources were measured, both with regex.

## Route A: the hand-written Exists helper

Pointer-typed parameters of `testAccCheck*Exists*` in the sibling `_test.go`:

| Result | Occurrences | Share |
|---|---:|---:|
| Authored type is among the helper's pointer parameters | 484 | 98.0% |
| Pointer parameters found, none match | 5 | 1.0% |
| Helper found, no pointer parameter | 4 | 0.8% |
| No sibling `_test.go` | 1 | 0.2% |

The dominant bucket counts "authored type appears among the pointer parameters." A real rule would filter `*testing.T` and `*terraform.State` to reach a single candidate. Route A resolves about 98% of occurrences.

## Route B: finders in the resource's own file

Distinct return types of `find*` functions declared in the same file:

| Result | Occurrences | Share |
|---|---:|---:|
| Exactly one finder return type in the file | 377 | 76.3% |
| No `find*` function in the file | 68 | 13.8% |
| Two distinct finder return types | 42 | 8.5% |
| Three or more | 7 | 1.4% |

Of the 426 occurrences with at least one finder in the file: 364 (85.4%) have a single finder type equal to the authored type, 45 (10.6%) have the authored type among several candidates, 17 (4.0%) have an authored type not among the file's finder return types. Route B resolves about 74% of all occurrences.

Route A's Exists helpers live in `_test.go`, which the shared generator walker excludes (`common/ast.go:119`, see [generators.md](generators.md)). Route B's finders are in production files.

## A wrong derivation is a compile error

The generated test declares the variable and passes its address to the hand-written helper:

```go
var v timestreaminfluxdb.GetDbInstanceOutput
...
testAccCheckDBInstanceExists(ctx, t, resourceName, &v),
```

A derived type that disagrees with the helper's parameter fails to compile, in generated code in the same package. This sets `existsType` apart from `Name`, where a wrong derivation silently relocates 685 fixture directories ([provider-contract.md](provider-contract.md)), and from `TypeName`, where it is a silent breaking change to a public API (see [silent-failures.md](silent-failures.md)).

## Cases no rule resolves

These require explicit authoring:

- `existsType` is not always a struct type. `iam/role_policy.go` and `iam/user_policy.go` author `string`; `dynamodb/table_item.go` authors a map of a type; `sqs/queue.go` authors a map keyed by an enum.
- Authored values are not consistent between an API wrapper output and the inner type. `paymentcryptography/key.go` authors `GetKeyOutput` where its finder returns `Key`; `cloudfront/key_value_store.go` authors `KeyValueStore` where its finder returns `DescribeKeyValueStoreOutput`. Both compile, because each matches its own Exists helper.

## The Exists helpers

Measured 2026-10-08:

| | Value |
|---|---|
| `testAccCheck*Exists` helpers in `internal/service` | 1,653 |
| whose body calls a `find*` function | 1,539 (93.1%) |
| median body length | 21 lines |
| bodies of 20 lines or fewer | 503 (30.4%) |

Roughly 35,000 lines of hand-written test scaffolding. What varies between them is the AWS type, the service client accessor, the finder function, and which state attributes the finder takes. 93.1% already name a `find*` function whose signature supplies three of those four. The finder lives in production code, so reading finder signatures is not blocked by the test-file exclusion in `common/ast.go:119` (see [generators.md](generators.md)).
