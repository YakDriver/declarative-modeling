# Should a fact exist at all?

Before choosing how to represent a fact, ask whether anyone needs to author it. The cheapest fact is the one nobody writes (see [derive-before-authoring](../../concepts/derive-before-authoring.md)). The same authored key can be removed, kept, or made automatic by several different moves, and they remove different amounts.

## The moves

| Move | What changes | Good | Bad |
|---|---|---|---|
| Derive from an authoritative fact | The consumer reads the source fact and the copy is deleted (`tagsTest` follows from `@Tags`) | One source of truth; removes 216 `tagsTest` lines | Needs the source to be complete |
| Dissolve by a generic consumer | The fact is never needed because the consumer infers it: a generic Exists check takes the finder and infers its result type | Strongest form of "Deletes inferable data instead of moving it": nothing authored, derived, or read, and no generator involved. Retires `existsType` and bears on 1,653 Exists helpers, ~35,000 lines, 93.1% of which already call a `find*` ([exists-type](../findings/exists-type.md)) | The consumer must be expressible generically; varied finder signatures need an escape. Touches `_test.go` at scale instead of regenerating |
| Default per resource kind | Policy supplies a value; only exceptions are written | Only overrides survive | `generator` is already defaulted, and its 163 uses are all overrides, so nothing shrinks |
| Default and strip values already at default | The marshaller omits any value still at its default, so the surface shrinks each time a default lands, not only for new resources (see [derive-before-authoring](../../concepts/derive-before-authoring.md)) | Largest candidate `identifierAttribute="arn"`, 659 of 1,053 `@Tags` lines; region is already unauthored at 88% ([registration](../findings/registration.md)) | Needs a one-time codemod and a rule for when a default later changes; three-state keys still need absent told apart from false |
| Override only where needed | Minimal authored data | Still needs a place to put the overrides |
| Infer from a convention | A heuristic reads naming or structure, with overrides (`existsType` from a finder's return type) | Could remove 492 lines; a wrong guess can't be silent, because the generated test declares `var v <Type>` and a mismatched type fails to compile | Couples the generator to code conventions; the accurate source is in `_test.go`, excluded today ([generators](../findings/generators.md)); 1-2% of values are not struct types |
| Keep as written | No new logic | Keeps the volume and the typo exposure |
| Ask the built object at startup | The provider inspects the constructed resource; embedded region and import markers are already visible there | The provider checks these at startup today | Runtime only, so generators can't use it; the tags identifier and identity attributes are not visible on the object |

None of these is ruled out or parked. They combine per fact: one fact can be derived while another is defaulted or kept.

## Which facts each move could reach

Volumes are from [registration](../findings/registration.md) and [testing-keys](../findings/testing-keys.md).

| Fact | Volume | A possible source |
|---|---:|---|
| `Name` (friendly) | 2,679 | Inferred ~91% from the factory name; misses are judgment names ("Hosted Zone", "Route Table") |
| `Region` | 2,679 | Defaulted (88% say the default) |
| `Factory` | 2,679 | Inferred if factories are discoverable; it is the function the declaration sits next to |
| `existsType` | 492 | Inferred from a finder's return type, a type argument, or dissolved by a generic check |
| `preIdentityVersion` | 336 | Authored (historical) |
| `tagsTest` | 216 | Derived from tags plus service wiring |
| `generator` | 163 | Defaulted; all uses are overrides, so nothing is left to remove |
| `hasNoPreExistingResource` | 126 | Authored (historical) |
| `TypeName` | 2,679 | Authored; inferable for 84.4%, but a wrong derivation is a silent breaking change to a public contract |

Role decides which move applies. A switch like `tagsTest` can be derived; a historical fact like `preIdentityVersion` cannot, because no running program holds last quarter's version. [testing-keys](../findings/testing-keys.md) sorts all 54 `@Testing` keys by whether a running program could supply them, and 51.2% cannot.

## Why "fails early" sorts the derivations

A derivation is only safe when a wrong result fails loud (see [divergence-is-not-configuration](../../concepts/divergence-is-not-configuration.md)). `existsType` clears that bar: a bad type is a compile error in the same package. `Name` does not, because a wrong derivation silently relocates 685 fixture directories ([provider-contract](../findings/provider-contract.md)). `TypeName` does not either, because a wrong value silently changes a public contract ([silent-failures](../findings/silent-failures.md)). The "Fails early, locally, and never inertly" criterion is what separates a derivation worth running from one that only hides the mistake.

## `existsType`, the clearest case

The finder already states the type:

```go
func findDBInstanceByID(ctx context.Context, conn *timestreaminfluxdb.Client, id string) (*timestreaminfluxdb.GetDbInstanceOutput, error) {
```

so this line could go away:

```go
// @Testing(existsType="github.com/aws/aws-sdk-go-v2/service/timestreaminfluxdb;timestreaminfluxdb.GetDbInstanceOutput")
```

The structured resource (timestreaminfluxdb DB instance) has two `find*` functions in its file, so the rule has to pick the right one and refuse when it can't. Whether the generator may read `_test.go` (the Exists-helper route, 98%) or must stay with production finders (the finder route, 74%) is unresolved ([exists-type](../findings/exists-type.md), [generators](../findings/generators.md)).
