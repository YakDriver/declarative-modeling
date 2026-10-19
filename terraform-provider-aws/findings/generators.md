# Generators and type loading

What the provider's code generators parse, how they run, what they emit, and the cost of loading the code with types. Counts are from this repository on 2026-10-01 unless noted: the `_gen_test.go` survey is 2026-10-06, type loading is undated (one developer machine, warm build cache), and the shared-layer counts are 2026-10-15. Counts exclude `_test.go` and generated files unless noted.

## Annotation parsing

Annotations are Go comment markers (`// @SDKResource("aws_...")`) parsed by the generators. The parsing surface, in lines:

| File | Lines |
|---|---:|
| `internal/generate/servicepackage/main.go` | 764 |
| `internal/generate/tagstests/main.go` | 769 |
| `internal/generate/identitytests/main.go` | 808 |
| `internal/generate/tests/annotations.go` | 722 |
| **Total** | **3,063** |
| `internal/generate/common/resource_identity.go` (shared identity parsing) | 415 |
| `internal/generate/common/args.go` (`ParseArgs`) | 56 |

Each of the three generators runs its own `ast.Walk` visitor over the same comments. `servicepackage/main.go` carries about 40 `v.errs = append(...)` semantic checks.

All three enumerate files through `internal/generate/common/ast.go:119`, which skips three things:

```go
// Skip directories, test files, and service_package_gen.go.
if entry.IsDir() || !strings.HasSuffix(entry.Name(), ".go") || strings.HasSuffix(entry.Name(), "_test.go") || entry.Name() == "service_package_gen.go" {
```

So no generator can see an annotation in a `_test.go` file. `service_package_gen.go` is excluded so a generator never reads its own output. Unknown keys and absent keys are both silent (see [silent-failures.md](silent-failures.md)).

The `*_gen_test.go` population (2026-10-06):

| | Count |
|---|---:|
| `*_gen_test.go` files in `internal/service` | 1,228 |
| of those, containing a `Code generated` header | 1,228 |
| hand-written files matching `*_gen_test.go` | 0 |

They fall into five families: `*_identity_gen_test.go` (520), `*_tags_gen_test.go` (357), `*_endpoints_gen_test.go` (260), `tags_gen_test.go` (85, per service), `tag_gen_test.go` (6). No hand-written `_test.go` under `internal/service` contains a line matching `^//\s*@[A-Z]`.

Registration markers each generator reads:

| Generator | Reads |
|---|---|
| `servicepackage` | resource and data-source markers, `Tags`, identity markers |
| `tagstests` | resource and data-source markers, `Tags` |
| `identitytests` | resource and data-source markers |

## Generator inventory

- 29 directories under `internal/generate`.
- 8,227 lines of Go (7,933 excluding tests); 62 templates.
- 3 test files, all in `common/` (`args_test.go`, `strings_test.go`, `version_test.go`). 28 of 29 generator directories have no tests, including all three annotation parsers.
- Build tags on `main.go`: 22 `//go:build generate`, 1 `//go:build ignore`, 1 `//go:build ingore` (`paginator/main.go:4`, a typo; it works because no build sets `ingore`).

## Invocation

941 `//go:generate` directives in `internal/service` (967 in all of `internal`), each a separate `go run`.

| Generator | Directives |
|---|---:|
| `servicepackage` | 274 |
| `identitytests` | 274 |
| `tags` | 238 |
| `tagstests` | 96 (97 services' `generate.go` mention it; savingsplans' line is commented out) |
| `listpages` | 48 |
| `tagresource` | 6 |
| `servicepackages` | 2 |
| `paginator` | 2 |
| `sweeperregistration`, `namevaluesfilters`, `awsclient` | 1 each |

`tags` directives use 54 distinct flags; the most common are `UpdateTags` (227), `ListTags` (212), `ServiceTagsSlice` (127), `KVTValues` (115), `ServiceTagsMap` (110).

Scoped versus full runs: `make gen PKG=xyz` runs `go generate` for that one service directory only (`$(GO_VER) generate $(SVC_DIR)/...`). That regenerates the service's `service_package_gen.go`, so a new resource in an existing service is registered without a full run. It does not regenerate provider-level files (`internal/provider/sdkv2/service_packages_gen.go`, sweepers), so a new service package, a change under `internal/generate/`, or a `names_data.hcl` edit needs full `make gen`. `servicepackage` reads `names_data.hcl` on every scoped run (`data.ReadAllServiceData()`). `gen-raw` runs provider-level generation last because the list depends on the per-service generated files existing. `gen-check` fails CI if generated output differs from what is committed. See [registration.md](registration.md) for the registration entries this produces.

## Generated output

| Artifact | Count |
|---|---:|
| `*_gen.go` in `internal/service` | 843 |
| `service_package_gen.go` | 274 |
| `*_gen_test.go` in `internal/service` | 1,223 |
| of which identity | 518 |
| of which tags | 355 |
| of which endpoints | 260 |
| `testdata` templates (`.gtpl`) | 764 |
| `testdata/*.tf` | 4,063 |

Volume of the generated tests is covered in [generated-tests.md](generated-tests.md).

## Type loading

A throwaway `go/packages` probe, warm build cache, one developer machine. Cold cache not measured.

| Run | Time | Notes |
|---|---|---|
| `make gen PKG=ecs` today (6 directives) | ~5 s | developer baseline |
| `servicepackage` on `ecs` | ~0.06 s | parse-only |
| `ecs`, `NeedTypes` (export data) | ~1.0 s | 0 unexported package vars visible |
| `ecs`, typed syntax | ~1.9 s | unexported vars visible |
| 278 service packages, typed syntax, one `Load` | ~4-6 s | 2.0-2.3 GB peak RSS |
| `ecs` + overlay with a stale reference to a deleted symbol | ~3.6 s | registration still discovered with 2 type errors |

Derived: per-package typed loading across 274 packages is roughly 9 minutes. `go/types` continues past type errors.

## The shared common layer

Measured 2026-10-15.

| | Count |
|---|---:|
| Generator directories | 29 |
| Importing `internal/generate/common` | 26 |
| Reading annotation keywords (`Keyword[...]`) | 5 |

The five keyword readers are `common`, `identitytests`, `servicepackage`, `tagstests`, and `tests`. Discounting `common` (the shared layer) and `tests` (a shared annotation helper), three generators consume annotations: registration, tag tests, and identity tests.

`internal/generate/common` is 1,227 lines. Within it, `resource_identity.go` is 415 lines and is a normalized, concern-specific model:

```go
type ResourceIdentity struct { … }

func (r ResourceIdentity) HasResourceIdentity() bool
func (r ResourceIdentity) IsARNIdentity() bool
func (r ResourceIdentity) IsParameterizedIdentity() bool
func (r ResourceIdentity) IsSingletonIdentity() bool
func (r ResourceIdentity) IdentityAttribute() string
…
```

It is imported by exactly the three annotation-consuming generators. One intermediate model for identity already sits between the annotations and those three consumers, not across all 29 generator directories.
