# `@Testing` annotation keys

Inventory of the keyword-argument keys on `@Testing` annotations in terraform-provider-aws, and a classification of each key by whether its value could be recovered from the running program. Inventory counted 2026-10-01; classification recounted 2026-10-05 at commit `fa1e8149e08`. Annotation lines counted with `rg '^//\s*@<Marker>' internal/service --type go`.

## Inventory

As of 2026-10-01: 2,275 `@Testing` lines ([surface.md](surface.md)), **54** distinct keys in use, **113** lines carrying more than one key. Counts are key occurrences.

| Count | Key | | Count | Key |
|---:|---|---|---:|---|
| 491 | `existsType` | | 7 | `tlsKey` |
| 336 | `preIdentityVersion` | | 7 | `existsTakesT` |
| 216 | `tagsTest` | | 7 | `domainTfVar` |
| 163 | `generator` | | 7 | `destroyTakesT` |
| 139 | `importIgnore` | | 6 | `useAlternateAccount` |
| 136 | `serialize` | | 6 | `requireEnvVarValue` |
| 126 | `hasNoPreExistingResource` | | 6 | `preCheckWithRegion` |
| 117 | `preCheck` | | 5 | `altRegionTfVars` |
| 114 | `importStateIdAttribute` | | 4 | `tlsKeyDomain` |
| 86 | `importStateIdFunc` | | 4 | `identityTestCases` |
| 69 | `plannableImportAction` | | 3 | `altRegionProvider` |
| 44 | `tagsIdentifierAttribute` | | 2 | `v60RefreshError` |
| 37 | `idAttrDuplicates` | | 2 | `subdomainTfVar` |
| 35 | `skipEmptyTags` | | 2 | `serializeDelay` |
| 34 | `checkDestroyNoop` | | 2 | `randomBgpAsn` |
| 24 | `identityVersion` | | 2 | `emailAddress` |
| 23 | `importStateIdAttributesSep` | | 1 | `v60NullValuesError` |
| 23 | `importStateIdAttributes` | | 1 | `tlsEcdsaPublicKeyPem` |
| 19 | `skipNullTags` | | 1 | `tagsUpdateGetTagsIn` |
| 17 | `identityTest` | | 1 | `tagsUpdateForceNew` |
| 17 | `identityRegionOverrideTest` | | 1 | `tagsTests` |
| 13 | `name` | | 1 | `sshKeyPair` |
| 12 | `tagsResourceType` | | 1 | `serializeParallelTests` |
| 12 | `preCheckRegion` | | 1 | `requireEnvVar` |
| 8 | `hasExistsFunction` | | 1 | `randomIPv4Address` |
| | | | 1 | `noRemoveTags` |
| | | | 1 | `importStateId` |
| | | | 1 | `acmSubdomainTfVar` |
| | | | 1 | `acmRootDomainTfVar` |

- **13** keys are used exactly once.
- `generator`: **129** `false` and **34** custom functions. The default, `acctest.RandomWithPrefix`, is never written explicitly.
- Four keys are read by `servicepackage`, not only by the test generators: `preIdentityVersion`, `hasNoPreExistingResource`, `v60RefreshError` (validation), and `v60NullValuesError` (production output). `servicepackage/main.go` lines ~445 to 507 carry a TODO to move them out of `@Testing`. See [provider-contract.md](provider-contract.md).

## Classification by kind of information

Recounted 2026-10-05 at commit `fa1e8149e08`: 7,034 annotation lines, 2,280 `@Testing` lines (the inventory above counted 2,275), `existsType` 492 (491), `preIdentityVersion` 337 (336). **2,402 keyword occurrences** across 54 distinct keys.

One question per key: could the value be recovered from the running program (the constructed resource, its schema, or the type system)? Four kinds answer no.

| Kind | Why it can't be recovered | Keys | Occurrences | Share |
|---|---|---:|---:|---:|
| History | Facts about past provider versions; not present in today's program at any time | 5 | 490 | 20.4% |
| Explicit switch | A decision nothing in the program prescribes | 5 | 415 | 17.3% |
| Environment | Facts about the external world: credentials, domains, keys, accounts | 19 | 186 | 7.7% |
| Execution policy | How the test run is scheduled, not what the resource is | 3 | 140 | 5.8% |
| Outside the four kinds | | 22 | 1,171 | 48.8% |

Not recoverable from the program: **32 of 54 keys, 1,231 of 2,402 occurrences (51.2%)**.

Members of each kind (per-key counts are in the inventory table above):

- **History:** `preIdentityVersion`, `hasNoPreExistingResource`, `identityVersion`, `v60RefreshError`, `v60NullValuesError`.
- **Explicit switch:** `tagsTest`, `generator`, `identityTest`, `identityRegionOverrideTest`, `tagsTests` (the single typo of `tagsTest`; see [silent-failures.md](silent-failures.md)).
- **Environment:** `preCheck`, `preCheckRegion`, `tlsKey`, `domainTfVar`, `useAlternateAccount`, `requireEnvVarValue`, `preCheckWithRegion`, `altRegionTfVars`, `tlsKeyDomain`, `altRegionProvider`, `subdomainTfVar`, `randomBgpAsn`, `emailAddress`, `tlsEcdsaPublicKeyPem`, `sshKeyPair`, `requireEnvVar`, `randomIPv4Address`, `acmSubdomainTfVar`, `acmRootDomainTfVar`.
- **Execution policy:** `serialize`, `serializeDelay`, `serializeParallelTests`.

The other 22 keys fall outside the four kinds; whether each is recoverable is unmeasured.

`existsType` is 492 occurrences, **20.5% of all keyword occurrences**, more than the Environment and Execution policy kinds combined. It names the resource's Go type as a string for the generated exists-check (see [exists-type.md](exists-type.md)). The next largest key outside the four kinds is `importIgnore`, 139 (5.8%).

`preIdentityVersion` and `hasNoPreExistingResource` (463 occurrences, 19.3%) are History and are among the keys `servicepackage` validates ([provider-contract.md](provider-contract.md)).
