# Scope and migration

How much of the annotation surface to change, in what unit, and how to get there without a flag day. Four separate decisions; none settled by measurement.

## How much to change

The surface spans registration, tags, region, identity, import, and the `@Testing` keys ([surface](../findings/surface.md)). The range runs from touching nothing to rewriting every resource at once.

| Option | What changes | Good | Bad |
|---|---|---|---|
| Leave it alone | Nothing | No migration, no new concepts; the 2,679 registrations keep working | Keeps silent unknown keys ([silent-failures](../findings/silent-failures.md)), three parsers, the 54-key `@Testing` surface |
| Tidy in place | The parser rejects unknown keys and malformed markers; syntax unchanged | Small; closes the silent-failure class; helps every later option; no retraining | Leaves density, discoverability, generator size, production/test mixing; invests in a language that may be replaced |
| Move only test facts | `@Testing` leaves production files; registration untouched | Targets the largest surface (2,275 lines, [surface](../findings/surface.md)) | Two systems to learn; not a clean cut, because some `@Testing` keys ship in the binary or gate `make gen` ([provider-contract](../findings/provider-contract.md)) |
| Migrate by family | One concern at a time (tags, then identity, and so on) | Incremental; each family takes the home that suits it | Coexistence machinery for the duration; retiring a family needs all its entries and consumers moved |
| Replace wholesale | Every resource, every consumer at once | One system, one vocabulary | 2,670 files in one change; no fallback |
| Split by plugin framework | Framework resources use their `Metadata` method and interfaces; SDKv2 keeps (frozen) annotations | New resources are Framework, so SDKv2 only shrinks | Two mechanisms at once; generators still need Framework names at generate time. Gated on the uniformity judgment in [criteria](criteria.md) |

Tidy in place and move-only-test-facts treat the mechanism as sound and the contents as the problem. The rest treat the mechanism itself as the thing to replace. The "migrates incrementally" hard constraint in [criteria](criteria.md) rules out replace-wholesale on its own.

## Migration unit

If change happens, what moves together. The unit is independent of the representation chosen ([representation](representation.md)).

| Unit | What moves together | Good | Bad |
|---|---|---|---|
| Resource | All production metadata for one resource, from one source; declaring it both ways is a generate-time error | No merge logic; mixed-state services allowed; a byte-identical index is the check | `@Testing` stays annotation-backed meanwhile |
| Concern family | One annotation family across a service (every `@Tags`, say) | Fine-grained; registration need not move first, given a binding by (kind, type name) | Per-field precedence; needs "unset" versus "empty", which Go zero values can't express (`common.TriBoolean` exists for this) |
| Service | A whole service at once | Simple union | No staging inside a service |
| Big bang | Everything | No coexistence code | 2,670 files at once |

Two things cut across the choice:

- Family order isn't forced by dependency. If a family binds to a still-annotated resource by (kind, type name), a simple family can migrate while registration stays in comments.
- Retirement is a separate, expensive gate. Removing a family's reader needs every entry and consumer moved: registration 2,679, `@Tags` 1,051, `@Testing` 2,275 lines ([surface](../findings/surface.md)). Gating one family on retiring another means finishing one of those first.

### Candidate slices

An inventory of pilot services, not an order.

| Slice | Shape | Exercises | Doesn't exercise |
|---|---|---|---|
| the simple resource (cloudsearch domain) | 2 SDKv2 resources, one annotation each | Discovery, coexistence, the reader, registration parity | Test generators |
| computeoptimizer | 2 Framework resources, registration only | The same, on the other framework | Test generators |
| the structured resource (timestreaminfluxdb DB instance) | 12 annotations, `@Tags`, `@IdentityAttribute`, `@Testing`; 4 generated test files | Tags, identity, test generation | Aliases, naming exceptions |
| comprehend | 12 annotations, SDKv2, ARN identity, a v6.0 compatibility marker | Compatibility markers, ARN identity | Framework |
| the exception (elbv2 load balancer) | Aliases, ARN identity, 29 naming misses | Aliases and naming overrides | A small blast radius |

## Feeding test generators during migration

Three generators consume annotations, and they already share one layer for identity ([generators](../findings/generators.md)). The premise that every generator must learn every representation is rejected ([ruled-out](ruled-out.md)); the real burden is three consumers. If production metadata moves, those generators still need the identity attribute and the fixture directory they embed in generated code ([generated-tests](../findings/generated-tests.md)).

| Option | Good | Bad |
|---|---|---|
| Interpret the moved form at generate time | Byte-identical tests | The generator gains an interpreter for the new form |
| Keep duplicate annotations for the generators | No interpreter | Two sources for one fact (breaks one-definition-one-authority in [criteria](criteria.md)); drift |
| Intermediate file dumped by a runtime pass | No interpreter | Committed artifact; it runs code to produce generator inputs ([intermediate-model](../../concepts/intermediate-model.md)) |
| Thin runtime wrappers | No interpreter; one source | Generated test files change |
| Derived names | `Name` and `TypeName` from a shared rule | Names only, not identity or import values; `TypeName` derivation is parked, discovery isn't ([discovery-and-placement](discovery-and-placement.md)) |

## Migration mechanics

How files actually change.

| Option | Good | Bad |
|---|---|---|
| One-shot codemod from the existing literal output | Mechanical; reproduces exact values | Throwaway tool |
| Generator mode that rewrites resource files | Reusable | A generator editing hand-written files raises ownership and idempotency problems |
| Agents migrate by hand | No tooling | Inconsistent; slower to verify |
| Delete markers (parked) | Migration becomes removal for conventional resources | Registration only |
| `skaff` emits the new form | New resources born migrated | Needs the reader to exist first |
| Declaration-form lint rule (parked) | Keeps syntactic discovery viable | Another lint; only the AST-discovery path needs it |
| Freeze the annotation language | The old system only shrinks | Blocks new markers people may want |
| Analyzer with suggested fixes | Reports missing or inconsistent metadata in the editor and via `go fix`; `.ci/providerlint` already hosts analyzers | An authoring aid, not a representation; sees only static facts |

A codemod on the simple resource (cloudsearch domain), acceptance being that `make gen` leaves the generated index unchanged. The form shown is one parked representation ([representation](representation.md)); the mechanics apply to any target form:

```diff
-// @SDKResource("aws_cloudsearch_domain", name="Domain")
+var domainRegistration = inttypes.ServicePackageSDKResource{
+	Factory:  resourceDomain,
+	TypeName: "aws_cloudsearch_domain",
+	Name:     "Domain",
+}
 func resourceDomain() *schema.Resource {
```
