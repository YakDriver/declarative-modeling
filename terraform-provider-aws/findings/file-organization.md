# File organization

Where typed Go declarations could live in `internal/service/*`, and what aggregating them into per-service files costs in navigation, diffs, and merge conflicts. Measured 2026-10-08.

Go imposes no constraint. Every file in `internal/service/kms/` compiles into one package, so file boundaries carry no semantics. The choice is navigation, diff locality, and merge conflicts, nothing else.

## Per-service aggregate files already exist

Hand-written per-service aggregate files exist today, with very different outcomes by size:

| File | Services | Median lines | Max |
|---|---:|---:|---:|
| `generate.go` | 279 | 9 | 21 |
| `exports.go` | 20 | 10 | 41 |
| `sweep.go` | 197 | 112 | 3,475 |

`sweep.go` is the existing experiment in aggregating one kind of thing per service. Its largest instance is 3,475 lines.

## Churn concentrates in aggregate files

Commits in the two years before 2026-10-08:

| File | Commits |
|---|---:|
| `ec2/service_package_gen.go` (2,264 lines, generated) | 241 |
| `ec2/exports.go` | 14 |
| `ec2/eip.go` | 0 |

`service_package_gen.go` is the generated per-service census of resources, data sources, and list resources. Its conflicts resolve by regenerating.

## Service size distribution

279 services, 8,799 `.go` files. Files per service: min 3, p25 11, median 20, p75 40, max 683 (ec2). Next largest: iam 185, s3 150, rds 136.

## Declaration referents cluster in the resource file

For the resources converted in the [list resource experiment](list-resource-experiment.md), the symbols a list declaration names sit mostly in the resource file, not the list file:

| Symbol | File |
|---|---|
| `resourceAlias` | `alias.go` |
| `findAliasByName` | `alias.go` |
| `resourceAliasFlatten` | `alias.go` |
| `listAliases` | `alias_list.go` |

ecr shows the same pattern: three of four referents in `repository.go`.
