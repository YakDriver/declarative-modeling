# Silent failures and where annotation keys are consumed

What happens when an annotation key is wrong or unread, and which keys cross between the test path and the production path. Measured on the provider repository at 2026-10-01; file:line references are from that reading.

## Silent-failure evidence

Nothing checks an annotation key against a list of known keys, so a wrong key does nothing and says nothing.

- Live silent typo: `internal/service/elasticache/reserved_cache_node.go:37` has `@Testing(tagsTests=false)`. No generator reads `tagsTests`; the key is `tagsTest`. The line is ignored without a warning. It is the only key in use that no generator reads.
- Unknown top-level markers produce `Warnf("unknown annotation")` and are dropped (`servicepackage/main.go:748`).
- Unknown keys are never checked. `common.ParseArgs` returns `map[string]string`, and consumers look up only the keys they know.
- Lines that fail the marker regex `^//\s*@([0-9A-Za-z]+)(\(([^)]*)\))?\s*$` are not treated as annotations at all.

## Key-to-consumer map

Every marker is read by `servicepackage`. `servicepackage/main.go:24` imports `internal/generate/tests` and calls `tests.ParseTestingAnnotations` (`main.go:447`), so all `@Testing` keys are parsed on the production path even when nothing in production uses them. Keys differ in where the value lands.

| Destination | Meaning | How to tell |
|---|---|---|
| Production output | Appears in `service_package_gen.go`, reaches the shipped binary | Field referenced in `servicepackage/service_package_gen.go.gtpl` |
| Generate-time validation only | Gates whether `make gen` succeeds; emitted nowhere | Read in `servicepackage/main.go` validation, absent from every template |
| Test output | Appears in `*_gen_test.go` only | Referenced in `tagstests`/`identitytests` templates |

### Markers by reader

| Marker | servicepackage | tagstests | identitytests | common |
|---|:-:|:-:|:-:|:-:|
| `@SDKResource`, `@SDKDataSource`, `@FrameworkResource`, `@FrameworkDataSource` | Y | Y | Y | – |
| `@Tags` | Y | Y | – | – |
| `@Testing` | Y | Y | Y | – |
| `@Region`, `@ArnFormat`, `@IdAttrFormat`, `@NoImport` | Y | – | Y | – |
| `@ArnIdentity`, `@IdentityAttribute`, `@SingletonIdentity`, `@CustomInherentRegionIdentity`, `@MutableIdentity`, `@ImportIDHandler`, `@IdentityVersion`, `@V60SDKv2Fix` | Y | – | – | Y |
| `@SDKListResource`, `@FrameworkListResource`, `@EphemeralResource`, `@Action`, `@CustomImport`, `@WrappedImport`, `@IdentityFix` | Y | – | – | – |

### Test-only keys living on production markers

Two keys sit on markers that otherwise describe production behavior, and are consumed only by a test generator.

| Key | Marker | Uses | Consumer | In production template? |
|---|---|---:|---|---|
| `attribute` | `@ArnFormat` | 7 | `identitytests/main.go:570` | No |
| `testNotNull` | `@IdentityAttribute` | 6 | `common/resource_identity.go` → `identitytests/resource_test.go.gtpl` | No |

`@ArnFormat`'s other key, `global=`, reaches production (`.IsARNFormatGlobal`), so that one marker carries one production key and one test-only key.

Every other key on a non-`@Testing` marker reaches production output: `global`, `duplicatesIdAttr`, `identityDuplicateAttributes`, `identifierAttribute`, `optional`, `overrideDeprecated`, `overrideEnabled`, `resourceAttributeName`, `resourceType`, `sdkV2IdentityUpgraders`, `setIDAttribute`, `validateOverrideInPartition`, `valueType`.

### `@Testing` keys that are not test-only

Four of the 54 `@Testing` keys:

| Key | Destination | Evidence |
|---|---|---|
| `v60NullValuesError` | Production output | `.HasV6_0NullValuesError` and `.WithV6_0SDKv2Fix` in `service_package_gen.go.gtpl` |
| `preIdentityVersion` | Validation only | Read at `servicepackage/main.go` ~484, ~493; absent from production template |
| `hasNoPreExistingResource` | Validation only | Read at `servicepackage/main.go` ~491, ~498; absent from production template |
| `v60RefreshError` | Validation only | Sets `PreIdentityVersion`; `V6_0RefreshError` absent from production template |

One `@Testing` key ships in the binary. Three others can fail `make gen` without appearing in any generated file.

### Keys whose meaning depends on the marker

| Key | Markers | Note |
|---|---|---|
| `name` | `@Action`, `@EphemeralResource`, `@FrameworkDataSource`, `@FrameworkResource`, `@SDKDataSource`, `@SDKListResource`, `@SDKResource`, and `@Testing` | On registration markers it is the friendly name that reaches production. On `@Testing` it overrides the name used for tests, which selects the `testdata/{Name}/` fixture directory (see [provider-contract](provider-contract.md)). |
| `identityVersion` | `@Testing` (20+ uses, compound `"0;v6.10.0"` form) | A separate top-level `@IdentityVersion` marker also exists (12 uses), with its own `sdkV2IdentityUpgraders` key |
| `global` | `@ArnFormat`, `@Region` | Same spelling, two different markers |
| `v60RefreshError` | `@Testing`, `@V60SDKv2Fix` | Readable from either marker |

`identifierAttribute`/`tagsIdentifierAttribute` and `resourceType`/`tagsResourceType` are near-duplicate spellings split across `@Tags` (production) and `@Testing` (test override).

### Keys with no consumer

One: `tagsTests`, the live typo in Silent-failure evidence above.

## Properties of key metadata items

Scope, when each item is consumed, and its shape. Sources: Key-to-consumer map above, [registration](registration.md), [provider-contract](provider-contract.md).

| Item | Scope | Consumed at | Shape |
|---|---|---|---|
| `TypeName` | resource | runtime (SDKv2 map key, Framework `Metadata`), generation (index, test files), startup validation | string; unique per kind, not across kinds; one factory may have several (aliases) |
| `Name` | resource | runtime (diagnostics only), generation (`testdata/{Name}/` path) | string |
| `Factory` | resource | runtime (called once at startup) | function value; one-to-many with `TypeName` |
| `Region` | resource | runtime (schema injection, interceptors) | one of 4 constructors plus `@Region` flags |
| `Tags` | resource | runtime (interceptors); generation (triggers tag tests where the service runs `tagstests`) | mode + identifier attribute + optional resource type |
| Identity attributes | resource | runtime (importers, interceptors); generation (identity tests) | ordered list |
| `IdentityVersion`, upgraders | resource | runtime | integer; slice of functions |
| `existsType` | resource | generation (tests only) | Go type, written as a string |
| `preIdentityVersion` | resource | generate-time validation; generation (upgrade tests) | provider version string |
| `hasNoPreExistingResource` | resource | generate-time validation; generation (upgrade tests) | boolean |
| `tagsTest` | resource | generation; cross-checked against `@Tags` | three-state (`TriBoolean`) |
| `generator` | resource | generation (tests only) | absent / `false` / function name |
| Tag-test generation enabled | service | generation | presence of a `tagstests` line in `generate.go` |
| Type-name prefix | service | generation | string or regex |

The scope column separates per-resource items from the two per-service items: whether `tagstests` runs, and the type-name prefix. See [registration](registration.md) for the prefix and for type-name uniqueness and identity-attribute ordering.
