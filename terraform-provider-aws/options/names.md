# Where the type name and friendly name come from

Each resource authors two strings: the public type name (`aws_ecs_service`) and a friendly name (`Service`). They are not the same kind of thing, so the right source can differ between them.

- The type name is the Terraform public API. A wrong value is a user-visible breaking change. `gen-check` surfaces any change in `service_package_gen.go`.
- The friendly name is diagnostic text at runtime and a directory name at generation time. A wrong value changes error text and, where tag or identity tests are generated, points a test at a fixture path that does not exist ([divergence-is-not-configuration](../../concepts/divergence-is-not-configuration.md)).

For a conventionally shaped, non-aliased resource, the only authored information not recoverable elsewhere may be the type name itself ([what-must-survive](../../concepts/what-must-survive.md)).

## Options

| Option | What changes | Good | Bad |
|---|---|---|---|
| Authored marker (today) | Nothing; one comment names both strings | Explicit; simple to parse | One line per resource (2,679) of mostly derivable data; untyped |
| Minimal marker, name derived | Author only the type name; derive the friendly name | Smaller; easy to make fail loud | Still one line per resource; still a comment language |
| Convention from the factory name (parked) | Derive both from the factory identifier; author an override only on exceptions | Zero authored lines for most resources; directive comments are how Go attaches small facts (`//go:`, `//nolint`) | A crude rule is 84.4% exact; misses cluster where the names-file prefix is a regex; ec2 legacy names and aliases need overrides; ties the public name to the Go identifier; needs a written tokenization rule ([derive-before-authoring](../../concepts/derive-before-authoring.md)) |
| Convention plus factory renames (parked) | Above, plus rename Go factories to fit the rule | Fewer overrides; agents make renames cheap | Does not help `aws_lb`/`aws_alb` or ec2 legacy names; large diff |
| Shim return type | Factories return a struct holding the name and the resource | Name travels with the resource in Go | ~1,750 SDK signature changes; Framework factories return a different type; generator still reads the literal |
| Name inside the factory body | Set the name in the constructor | No extra declaration | Generator must read function bodies, or the name exists only at runtime; the runtime-only form fails *serves every consumer* (generators need the name at generate time) |
| Metadata method on a separate type | A typed method supplies the name | Typed | No SDKv2 equivalent |
| Framework's native `Metadata` (parked) | Each Framework resource sets its own `TypeName`; the wrapper reads it from the inner resource | The framework's designated place; the inner resource already exists at wrap time; the Framework index could become a factory list | Generators need the name at generate time, so they parse `Metadata` bodies (the name-in-body problem); the base `Metadata` panics by design today; SDKv2 needs a separate mechanism. Parked until maintainers decide uniformity across frameworks is not required |
| Per-service override table in Go | A typed slice of overrides per service | Overrides in one typed place; per-concern locality | Funcs are not comparable map keys, so it is string-keyed or a generator-interpreted slice; overrides leave the factory file ([locality](../../concepts/locality.md)) |
| Runtime derivation via `FuncForPC` | Names computed at runtime from the function pointer | No generator involvement in naming | Fails *serves every consumer* (generators need names for test files and fixture paths); nothing checked at build time; public contract tied to Go identifiers |
| Derive from docs filenames | Read names from `website/docs/{r,d}` | Independent existing source (2,402 pages); usable as a cross-check under any option | Docs are not 1:1 with factories; another stringly source |
| Per-resource entries in the central names file | Declarative rows in `names_data.hcl` | Declarative; schema-validatable | Editing the central 10,037-line file needs full `make gen`, breaking the scoped loop; fails *resource-scoped work stays complete and fast* |
| `ResName` constants (rejected, see [ruled-out.md](ruled-out.md)) | Reuse existing `ResName` string constants | Already in some files | Error-message constants in the legacy `create.Error` pattern (1,853 uses), a subsystem smarterr is replacing; never a registration mechanism |
| Generic type parameter carrying the name | A type parameter holds the name | Typed | Go types cannot carry string constants; reduces to the shim return type |
| Hand-maintained list | A central explicit list of names | Fully explicit | Explicit-composition tradeoffs ([discovery-and-placement](discovery-and-placement.md)) |
| Derive from the source filename (parked) | `cloudsearch/domain.go` → `aws_cloudsearch_domain`; `_data_source.go` → data source | File naming is already a documented convention; survives Go identifier renames; generators already key test filenames and templates on the source filename ([declaration-placement](../../concepts/declaration-placement.md)) | Unmeasured; several resources per file breaks it; `vpc_.go`-style names need rules; renaming a file renames a public type |
| Typed constant beside the factory, found by convention | `const loadBalancerTypeName = "aws_lb"`, discovered by the generator | Typed; greppable; no comment syntax | Same shape as `ResName`; a naming convention the generator must know |

## Convention sketch

The simple resource (cloudsearch domain) and the structured resource (timestreaminfluxdb DB instance) author nothing:

```go
func resourceDomain() *schema.Resource {
```

The rule: strip `resource`/`new…Resource`, snake-case, prepend the `names_data.hcl` prefix, giving `aws_cloudsearch_domain` and `aws_timestreaminfluxdb_db_instance`; take the friendly name from the type-name suffix, giving "Domain" and "Db Instance". The structured resource's derived "Db Instance" differs from today's "DB Instance", which moves `testdata/DBInstance/` unless the rule handles acronyms or an override is written.

The exception (elbv2 load balancer) is authored as overrides, because its prefix is a regex (`aws_a?lb(...)`), not a string to prepend:

```go
// @TypeName("aws_lb", name="Load Balancer")
// @TypeName("aws_alb", name="Load Balancer")
func resourceLoadBalancer() *schema.Resource {
```

What makes the convention refuse rather than guess is open. Without a loud refusal, it fails silently on the one value whose errors reach users ([silent-failures](../findings/silent-failures.md)).

## Constraints on every option

- `gen-check` forces any type-name or friendly-name change into a committed diff ([registration](../findings/registration.md)). A dedicated "type name removed" check would make it explicit.
- The type name is not a unique key: 552 names register more than once, so the identifying key is (kind, type name). Aliases today are duplicate entries (`aws_alb`/`aws_lb`); an `Aliases` field is possible under any option ([provider-contract](../findings/provider-contract.md)).
- A derived friendly name touches 685 fixture directories, so the convention and source-filename options imply a directory rename sweep, a rule guaranteed to reproduce current values, or a fixture key that is not the friendly name.
