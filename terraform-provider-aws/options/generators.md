# How generators run, and the model behind them

These options change how the provider's code generators are invoked and how authored facts reach them, not how the facts are authored (that is [representation.md](representation.md)). They matter because the generators are where a silent key or a per-resource special case would have to be caught.

## How it runs today

941 `//go:generate` directives in `internal/service`, each a separate `go run`. Three of the 29 generators consume annotations (registration, tag tests, identity tests); each runs its own `ast.Walk` over the same comments, 3,063 lines of parsing in total. 28 of 29 generator directories have no tests. Ordering lives in Makefile sequence plus a comment, and `paginator/main.go` ships a `//go:build ingore` typo that works only because nothing sets that tag. Full counts in [generators findings](../findings/generators.md).

## Invocation

| Option | What changes | Good | Bad |
|---|---|---|---|
| One `go run` per directive (today) | nothing | no change | repeated parsing; implicit ordering; the scoped-vs-full trap |
| Single driver | one `go/packages` load, emitters become plain functions called in explicit order | one parse; ordering is code, not Makefile order; one path for scoped and full runs | large change; scoped mode must stay first-class or it regresses. Parked |
| Batched loads | load packages in bounded groups | bounded memory | more complex than one load |
| Shared library, today's topology | unify parsing, keep per-directive invocation | one parser without re-architecting | keeps the repeated work |
| Shared semantic model | each authoring form is a frontend producing one in-memory model per resource with source positions; emitters and validation read only the model | migration runs two frontends into one model; emitters don't change per form; validation runs once; see [intermediate-model](../../concepts/intermediate-model.md) | can become the next catch-all unless every field has a named consumer, the same hazard as [vocabulary-governance](../../concepts/vocabulary-governance.md) |

Single driver, in a service's `generate.go`:

```go
//go:generate go run ../../generate/driver
```

```go
func main() {
	pkgs := load(os.Args)     // one Load, scoped or full
	regs := discover(pkgs)
	emitServicePackage(regs)
	emitTags(regs)
	emitTagsTests(regs)
	emitIdentityTests(regs)
	if full {
		emitProviderLists(regs) // ordering is this line's position
	}
}
```

## Characterization tests first

Any invocation change is unverifiable today because the parsers have no tests. Three levels, cheapest first:

| Level | Covers |
|---|---|
| Unit | parser behavior: known keys, unknown keys, malformed markers, three-state values |
| Fixture-to-golden | a synthetic service in, expected generated files out, per generator |
| Real-service parity | one real service through all three generators together, where a shared reader's integration bugs hide |

Fixture-to-golden uses the running examples as input shapes:

```text
servicepackage/testdata/
  simple/domain.go                          # the simple resource (cloudsearch domain)
  simple/service_package_gen.go.golden
  structured/db_instance.go                 # the structured resource (timestreaminfluxdb)
  structured/service_package_gen.go.golden
```

The cost is up-front work before any visible change. The payoff is that every later change to the shared reader becomes CI-verifiable.

## Service-level metadata

Service-wide facts live in two places today: `names_data.hcl` (one central file) and `//go:generate` flags (`tags` alone uses 54 distinct flags, [generators findings](../findings/generators.md)). `service_package_gen.go` already mixes annotation data with `names_data.hcl` data.

| Option | What changes | Good | Bad |
|---|---|---|---|
| Keep as-is | nothing | no change | central file; editing it needs full `make gen`; flag DSL |
| Split the central file per service | one data file per service | service-data edits work under `make gen PKG=xyz` | many files |
| Fold generate flags into per-service data | the flag DSL becomes data | removes the DSL; makes the test-generation switch visible | generators must read the new source |
| Per-service Go declaration | typed per-service facts | typed | awkward for AWS-side facts (operation names, error codes) |
| Per-service HCL | one declarative file per service | declarative; fits AWS-side facts | another schema to maintain. Parked |

Per-service HCL, replacing a service's central-file block and its generate flags:

```hcl
service "timestreaminfluxdb" {
  resource_prefix = "aws_timestreaminfluxdb_"
  sdk_package     = "timestreaminfluxdb"

  tags {
    kvt_values = true
    list_tags  = true
    update_tags = true
  }

  generate {
    tags_tests     = true
    identity_tests = true
  }
}
```

## A normalized concern model

Independent of how facts are authored. Each annotation-consuming generator builds its own view today, except identity: all three share `common.ResourceIdentity`, a 415-line concern-specific model that already sits between the annotations and its three consumers ([generators findings](../findings/generators.md)).

| Option | What changes | Good | Bad |
|---|---|---|---|
| Status quo | per-generator parsing, one shared model by accident | nothing to build | each new form is learned three times; no single place to catch two authorities for one fact |
| Extend the existing pattern | add concern models in `common` for registration, tagging, test policy, as identity already does | follows a pattern already in the tree, under its own name; incremental, one concern at a time; one home for validation and duplicate-authority detection | still new surface: needs an owner, rules, and a stated lifetime for migration-era frontends |
| Full frontend/model architecture | many frontends resolving into one provenance-carrying model before any consumer reads it | change a fact's authority without touching consumers; provenance names the authoring site in errors | an indirection layer for a three-consumer problem, arriving on top of untested generators. The framing where every generator learns every form is [rejected](ruled-out.md) |

Provenance is the separable win. Recording where each fact came from is cheap independent of how much model gets built, and it does two things nothing else does: it makes one-fact-one-authority mechanically checkable, and it lets a diagnostic point at the line a contributor wrote. See [intermediate-model](../../concepts/intermediate-model.md) for why reporting a fact through a model does not move ownership into it.

What would decide between the middle and heavy options: whether a second concern normalizes in `common` without the model growing fields no consumer reads. If it lands as cleanly as identity did, the pattern holds; if it needs per-consumer escape hatches, the status quo is honest about something the model hides.

## Workflow comparison

How the authoring forms in [representation.md](representation.md) and [shared-implementation.md](shared-implementation.md) behave across the dev loop. The register and dev-loop steps are the same for every generate-time form (write the file, run scoped `make gen`), so the forms separate only on the rows below.

| Workflow | today's annotations | comment expressions | typed Go | runtime harness |
|---|---|---|---|---|
| Typo in a knob | often silent | compile error in generated file | compile error | compile error |
| Discover a resource's knobs | docs or generator source | docs; no completion | editor completion | editor completion |
| See one lever across resources | grep | grep | grep, or a per-service override file | a harness table |
| Provider-wide shape change | edit the generator template | codemod expressions in comments | codemod ~2,700 literals or calls | edit the harness |

The "often silent" cell is the status quo's one hard failure: unknown and absent keys are both dropped without a word ([silent-failures](../findings/silent-failures.md)). Every alternative turns that into a compile error.
