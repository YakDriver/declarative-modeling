# History of provider annotations

Timeline, the first annotation form, the documented motivations, and the growth of annotation lines in terraform-provider-aws. Dates come from `git log` on the provider repository, with commits cited inline. Growth counts are taken at the last commit before each listed date; the most recent is 2026-10-02. Motivations are quoted from issue #26626 (2022-09-02) and PR #28933 (merged 2023-02-22).

## Timeline

| Date | Event | Source |
|---|---|---|
| 2014-05-29 | Provider's first commit | `8570c8cda4d` |
| 2021-10 | Service package reorganization | PR 21306 |
| 2022-09-02 | Self-registration proposed | Issue #26626 |
| 2022 (prototype) | `init()` functions plus a per-package registry implemented | PR #28933 body |
| 2023-01-16 | Annotations prototyped: four bare markers, no arguments | `3d6fed20b9a`, `a5dfc405d41` |
| 2023-02-22 | Annotations merged, shipped in v4.56.0 | PR #28933 |
| 2023-03-01 | Keyword-argument parsing added, plus `@Tags` | `0744fe7e8e8`, `4cfa2c7cb52` |
| 2024-02-16 | `@Testing` introduced with the tags-test generator | `499c98d184a` |
| 2025-03-05 | `@Region`, first use: IPAM global resources | |
| 2025-04-02 | `@IdentityAttribute`, `@ArnIdentity`, first uses: `aws_s3_bucket`, `aws_batch_job_definition` | |
| 2025-04-04 | `@SingletonIdentity` | `aws_s3_account_public_access_block` |
| 2025-06-27 | `@V60SDKv2Fix` | `aws_s3_bucket` |
| 2025-07-21 | `@CustomImport` | `aws_s3_bucket` |
| 2025-10-27 | `@IdentityVersion` | `aws_sqs_queue` |

At 2026-10, annotations are 3 years 7 months old. The provider is 12 years old and the service package reorganization 5 years. The identity family is about 18 months old and the compatibility family about 15 months.

## The first form had no keyword arguments

The original four markers (`3d6fed20b9a`):

```go
frameworkDataSourceAnnotation = regexp.MustCompile(`^//\s*@FrameworkDataSource\s*$`)
frameworkResourceAnnotation   = regexp.MustCompile(`^//\s*@FrameworkResource\s*$`)
sdkDataSourceAnnotation       = regexp.MustCompile(`^//\s*@SDKDataSource\("([a-z0-9_]+)"\)\s*$`)
sdkResourceAnnotation         = regexp.MustCompile(`^//\s*@SDKResource\("([a-z0-9_]+)"\)\s*$`)
```

Framework markers carried no type name at all. SDK markers carried exactly one string and nothing else. There was no `name=`, no friendly name, no key/value space.

The keyword-argument sub-language arrived six weeks later (2023-03-01, `0744fe7e8e8`, "Add code to parse annotation arguments"), introduced to support `@Tags`. Every later key, including all 54 `@Testing` keys (see [testing-keys.md](testing-keys.md)) and the silent handling of unknown keys (see [silent-failures.md](silent-failures.md)), lives in a facility that was added for a different marker after the design shipped.

## The documented motivations

Issue #26626 states why the central map was left. The collection of resources was "statically defined in one source file (`provider/provider.go`)":

> A single source file referencing all implemented resources and data sources was the pragmatic solution when there were only a handful or few dozen implementations but becomes unwieldy (and a source of merge conflicts) when there are a few thousand.

The same issue documents the circular dependency:

> the provider needs to know about all its implemented resources and data sources and each of the resources and data sources need to know about the provider's configured state to access SDK service clients. This circular dependency is broken by maintaining two data structures in separate Go packages.

Its goals: reduce the steps to add a service and a resource; a more modular codebase minimizing God objects; support plugin muxing; support both AWS SDK versions in one service; minimize cross-package references to reduce build time; simplify sweepers; and "Implementation has to be gradual - No stop-the-world, big bang refactoring."

The issue listed `init()` and annotations as alternatives for the same job:

> Resources (and data sources) self-register (via `init()` function or "annotations" in conjunction with `go generate`) with a per-service resource registry

`init()` was built first. PR #28933 replaced it, and the reason it gives is not boilerplate reduction:

> The current prototype mechanism for resource self-registration relies on Go `init()` functions and a per-package registry. The HashiCorp Go style guide has this to say:
>
> > Always avoid using the `init()` function or calling functions to assign values to package-level vars. This package level state makes a function difficult to test, and impossible to reuse.

One constraint from #26626 applies to every option and has not changed:

> Due to Go's static linking philosophy, there must be (at least) one source location that references all the internal service packages. This can be done either via import statements (and init functions in the service packages) or explicitly via a per-service structure (or interface) reference

## Growth

Annotation lines in `internal/service`, counted as `^//\s*@[A-Z]` at the last commit before each date.

| Date | All annotation lines | `@Testing` |
|---|---:|---:|
| 2023-02-01 | 0 | 0 |
| 2023-04-01 | 1,667 | 0 |
| 2023-07-01 | 2,339 | 0 |
| 2024-01-01 | 2,480 | 0 |
| 2024-04-01 | 2,549 | 3 |
| 2025-01-01 | 3,349 | 418 |
| 2026-01-01 | 4,817 | 1,172 |
| 2026-10-02 | 7,025 | 2,275 |

Shape of the curve:

- Rollout was fast: 0 to 1,667 lines in roughly two months once the mechanism merged.
- Then nearly flat for about 9 months: 2,339 (Jul 2023) to 2,549 (Apr 2024), tracking new resources rather than new kinds of metadata.
- Then 2.75x in two and a half years: 2,549 to 7,025 since April 2024. The latest row matches the inventory in [surface.md](surface.md).
- `@Testing` accounts for about half of that growth: 2,272 of the 4,476 lines added since April 2024, and 32% of the current total. The identity and compatibility families account for most of the rest.
