# Where test facts live

`@Testing` carries 2,275 lines across 54 keys, produces none of its own output, and sits in production files ([testing-keys](../findings/testing-keys.md)). Three questions decide where it could go instead: where per-resource facts live, who switches generation on, and where test-only data lives. All three share one constraint: the test generators still have to be fed, and some keys fail `make gen` while appearing in no generated file ([provider-contract](../findings/provider-contract.md)).

The running example throughout is the structured resource (timestreaminfluxdb DB instance).

## Per-resource test facts

The facts are `existsType`, `importIgnore`, `importStateIdFunc`, `preCheck`, `serialize`, `generator`, and the rest of the 54 keys. Scenario counts are set by templates and are out of scope.

| Option | What changes | Good | Bad |
|---|---|---|---|
| Keep `@Testing` in the resource file (today) | Nothing | Works now | 54-key comment language; generators carry per-resource knowledge, against [generators don't know individual resources](criteria.md); a test lever lives in a production file |
| Move the `@Testing` comments to the test file | Same keys, relocated to `_test.go` | Smallest change that separates production from test; production file stops churning on test edits | The comment form keeps `existsType` as a Go-symbol string, which is **rejected** ([ruled-out](ruled-out.md)); binding to the resource needs the type name or factory; `common/ast.go:119` excludes `_test.go` from the parsers today, so relaxing it is an open decision; crossing keys like `preIdentityVersion` are still read by `servicepackage` ([provider-contract](../findings/provider-contract.md)) |
| Typed test spec, still generated | A Go literal beside the test feeds the generator | Data sits with the test; can name test-only symbols | The HCL variant references Go symbols as strings and is **rejected** ([ruled-out](ruled-out.md)); the Go form still needs a generator to read the literal, or the generated test to read it at runtime (which is the wrapper option below) |
| Runtime harness in a hand-written test | `_test.go` calls shared helpers; reads schema and identity at runtime | Typed; `existsType` becomes a type argument; `tagstests`/`identitytests` (~1,577 lines) mostly disappear | Large build; generated test cases become subtests, changing CI sharding and `make t T=…`; 4,063 `testdata/*.tf` still expand; risk of a 54-field spec; 51.2% of keyword occurrences are kinds no runtime inspection supplies ([testing-keys](../findings/testing-keys.md)) |
| Generated wrappers over a runtime harness | Generators emit thin `_test.go` wrappers that call the harness | Generators only discover, never interpret; works per migrated resource without the full harness | Generated test files change, so no byte-identical check ([generated-tests](../findings/generated-tests.md)); still generated |

`existsType` naming a Go type is the pivot: the type system already holds it ([exists-type](../findings/exists-type.md)), so the harness passes it as a type argument instead of a string.

```go
func TestAccTimestreamInfluxDBDBInstance_generated(t *testing.T) {
	acctest.RunResourceTests[timestreaminfluxdb.GetDbInstanceOutput]( // new
		t,
		dbInstanceRegistration,
		acctest.ResourceTestSpec{ // new
			ImportIgnore:          []string{"bucket", "username", "organization", "password"},
			PlannableImportAction: plancheck.ResourceActionReplace,
		},
	)
}
```

Tags and identity scenarios come from the registration; `existsType` is gone from the authored surface.

Writing scenarios once at runtime reduces generated test lines. That is a side effect, not a reason: apply counts are unchanged.

## Who decides whether tests are generated

Two switches exist today and neither validates the other: 437 `@Tags` files sit in services that never run the tag-test generator, and 4 opt-outs in those services are inert ([silent-failures](../findings/silent-failures.md)).

| Option | What changes | Good | Bad |
|---|---|---|---|
| Both switches, unvalidated (today) | Nothing | No change | `@Tags` implies tag tests in some services and not others; inert opt-outs |
| Both switches, cross-checked | A check fails on contradiction | Keeps both switches; contradictions become errors that name the line, satisfying [fails early, locally, and never inertly](criteria.md) | Two places to edit; needs a decision for each of the 121 non-invoking services |
| Per-resource switch only | Every service runs the generators; annotations decide | One switch, beside the resource | 121 services would generate tests where `testdata/tmpl/*_basic.gtpl` fixtures don't exist; needs explicit opt-outs first |
| Per-service switch only | `@Tags` never implies tests; a service setting does | One switch | Per-resource exceptions still need a home |
| Service-level data holds the switch | A service data file carries it | Visible as data, not a `go:generate` line | **Parked** (per-service data file); depends on that file existing |

The contradiction a cross-check would catch:

```text
db_instance.go:46: @Tags without tag tests: service does not run tagstests (add tagsTest=false to opt out)
```

## Where test-only data lives

`preIdentityVersion` (336 uses), `hasNoPreExistingResource` (126), and `v60RefreshError` (2) are read by `servicepackage` generate-time validation and by upgrade tests. They reach no production output, but moving them can break `make gen` ([provider-contract](../findings/provider-contract.md)). The reverse case also exists: `@ArnFormat(attribute=)` (7) and `@IdentityAttribute(testNotNull=)` (6) are test-only keys sitting on production markers, so a sweep of `@Testing` alone misses them.

| Option | What changes | Good | Bad |
|---|---|---|---|
| Production registration | Fields sit beside `IdentityVersion` | Near related identity history | Ships test-only data in the binary; a field no production code reads; still a production edit to change test behavior |
| Typed test spec | Data sits with its only reader | Co-located with the reader; the cross-check can run as a test | Needs the spec to exist (per-resource facts, above) |
| Stay in `@Testing` | Nothing | No change | Keeps the entanglement |
| Separate identity-history marker | A dedicated `@IdentityHistory` comment | Untangled from `@Testing` | Still a comment; a new marker |
| Derived from repository history | Read the pre-identity version from git or CHANGELOG | Nothing authored | Couples generation to repo history; wrong for resources whose identity changed; needs a source reliable for 336 resources |

One rule covers the direction: a field belongs in production registration only if production code reads it. That sorts `v60NullValuesError` (reaches production output, so not test-only) from the rest. See [spec-or-metadata](../../concepts/spec-or-metadata.md).

```go
Identity: inttypes.RegionalSingleParameterIdentity(
	inttypes.StringIdentityAttribute(names.AttrID, true),
	inttypes.WithPreIdentityVersion("v6.43.0"), // new, production registration
),
```

Deriving the version silently risks the same failure as deriving `Name`: a wrong guess points generated tests at a fixture path that doesn't exist. See [divergence-is-not-configuration](../../concepts/divergence-is-not-configuration.md).
