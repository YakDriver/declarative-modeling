# Generated test volume

What the test-generation annotations expand into across `internal/service`, measured on the provider repository as of 2026-10-01.

## Totals

| Measure | Generated tests | Hand-written tests | Production code |
|---|---:|---:|---:|
| Lines | 994,564 | 1,302,463 | 1,085,303 |
| Files | 1,223 | | |
| Test functions | 7,099 | | |
| Test cases (`resource.Test`/`ParallelTest`) | 6,860 | | |
| Apply steps (`Config`/`ConfigDirectory`) | 27,339 | 25,348 | |

Generated test code is 92% the size of all hand-written production service code (994,564 vs 1,085,303 lines). Generated tests are 52% of counted acceptance-test apply steps (27,339 of 52,687). Wall-clock time and AWS cost are not measured; steps vary widely in cost (one RDS or EKS create versus many cheap applies).

Also 4,063 `testdata/*.tf` files, expanded from about 764 templates.

## Blast radius of a single key

Measured by removing one annotation and regenerating. `@Testing(sshKeyPair=true)` appears exactly once, at `internal/service/ec2/ec2_key_pair.go:36`. Removing that line and running `make gen PKG=ec2` changed 21 tag tests, 4 identity tests, and 8 configuration files.

One annotation line can control tens of generated artifacts, including generated Terraform configuration. Nothing currently detects a change in that relationship.

The 8 changed configuration files separate keys that vary generated HCL from keys that vary Go test code. Generated configuration comes from templates, so `sshKeyPair` varies emitted HCL rather than only Go setup, despite having one use.

## Amplification per annotation line

| Generated kind | Files | Lines | Funcs | Apply steps | Avg lines/file |
|---|---:|---:|---:|---:|---:|
| `*_tags_gen_test.go` (per resource) | 355 | 675,641 | 5,364 | 21,369 | 1,903 |
| `tags_gen_test.go` (per service) | 84 | 1,752 | | 0 | 21 |
| `*_identity_gen_test.go` | 518 | 152,989 | 1,475 | 5,970 | 295 |
| `*_endpoints_gen_test.go` | 260 | | | | |

One `@Tags(identifierAttribute="arn")` line, where it generates tests at all, averages 1,903 lines, about 15 test functions, and about 60 AWS apply steps. Example: `timestreaminfluxdb/db_instance`, whose test-relevant input is three annotation lines (`@Tags`, `@IdentityAttribute`, `preIdentityVersion`):

| File | Lines | Test funcs |
|---|---:|---:|
| `db_instance_tags_gen_test.go` | 2,431 | 21 |
| `db_instance_identity_gen_test.go` | 325 | 4 |

The largest single generated test files run to about 2,600 to 2,700 lines each: `iam/server_certificate_tags_gen_test.go` 2,680; `networkmanager/site_to_site_vpn_attachment_tags_gen_test.go` 2,630; `kms/replica_key_tags_gen_test.go` 2,615.

1,051 `@Tags` annotations and 687 identity annotations exist, against 355 and 518 generated per-resource test files. Per-resource suppression (`tagsTest=false`, 215 uses) is part of the gap. The larger part is that test generation is opted in per service: 218 services carry `@Tags` and 97 invoke `tagstests` from `generate.go` (44%). 437 files with `@Tags` sit in the 121 services that never run it.

The annotation and the generator wiring are two independent switches, and neither validates the other. In a non-invoking service, `@Tags` drives production tagging and generates no tests.

Test-generation opt-outs in non-invoking services are inert: 4 lines, `tagsTest=false` in `sagemaker/model_card.go:45`, `sagemaker/labeling_job.go:45`, and `verifiedpermissions/policy_store.go:36`, plus the `tagsTests=false` typo (see [silent-failures.md](silent-failures.md)). The recognized key is `tagsTest` (`tagstests/main.go:579`). The typo is harmless only because elasticache never invokes `tagstests`; if it did, the opt-out wouldn't apply and generation would fail on the missing `testdata/tmpl/reserved_cache_node_basic.gtpl` (`tagstests/main.go:188`, `os.Exit(1)` at `:332`).

## Where the volume comes from

The expansion factor is set by the generators' templates (see [generators.md](generators.md)), not by the annotation author. How many scenarios one line becomes (tag CRUD, null and empty tags, computed tags, region override, import variants, upgrade tests per prior provider version) is a template decision applied uniformly. Two things are separate:

- Scenario count (why there are 27,339 applies) is encoded in templates plus suppression keys like `tagsTest`, `identityTest`, `identityRegionOverrideTest`, `identityTestCases` (see [testing-keys.md](testing-keys.md)).
- Per-resource facts (`existsType`, `importIgnore`, `importStateIdFunc`, `preCheck`, `serialize`, `generator`) are configuration a test needs.
