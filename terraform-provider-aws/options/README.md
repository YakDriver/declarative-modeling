# Options

Design options for replacing the provider's resource annotations. One file per question below; each option says what would change, a short code sketch where it helps, and what is good and bad about it. Nothing here is chosen.

The fourteen criteria for comparing options are in [criteria.md](criteria.md).

## The questions

| Question | Range of answers | Where |
|---|---|---|
| How much should change at all? | Leave it; tidy in place; move only test config; migrate by family; replace wholesale; split by plugin framework | [scope-and-migration.md](scope-and-migration.md) |
| Should a given fact be authored at all? | Derive; default; override; infer by heuristic; ask the constructed object at startup; keep | [should-facts-exist.md](should-facts-exist.md) |
| How are the type name and friendly name authored? | Today's marker; minimal marker; convention plus override (factory name or source filename); Framework's native `Metadata`; shim types; override tables; derive from docs, `names_data.hcl`, or runtime | [names.md](names.md) |
| How is structured metadata (tags, identity, import) represented? | Typed marker table; Go directives; pass-through Go expressions; Wire-style calls; authored literal; typed constructor; sidecars; HCL; interface methods; embedded types | [representation.md](representation.md) |
| How are declarations found? | Interpret literals; import and read; syntactic or type-resolved discovery; explicit per-service composition root; convention only | [discovery-and-placement.md](discovery-and-placement.md) |
| Where do per-resource test facts live? | Keep in the resource file; move the same comments to `_test.go`; typed sidecar; runtime harness; generated thin wrappers | [test-facts.md](test-facts.md) |
| Who enables test generation? | Today's two switches; cross-checked; per resource; per service; service data | [test-facts.md](test-facts.md) |
| Where does test-only data belong? | Production registration; test spec; stay; separate marker; derive from history | [test-facts.md](test-facts.md) |
| What is the unit of migration? | Resource; family; service; big bang | [scope-and-migration.md](scope-and-migration.md) |
| How do test generators work during migration? | Interpret; duplicate; intermediate file; thin wrappers; derived names | [scope-and-migration.md](scope-and-migration.md) |
| What mechanics perform the migration? | Codemod; rewriting generator; agents; delete markers; `skaff`; lint; analyzer with fixes; freeze | [scope-and-migration.md](scope-and-migration.md) |
| How should invalid declarations fail loud? | Per-consumer; shared key list; full table; malformed-line errors; report-only; analyzer | [validation.md](validation.md) |
| Where does validation run? | Generator; `Validate()`; collection checks; startup; `go/analysis` | [validation.md](validation.md) |
| How are generators invoked? | Today; single driver; batched; shared library; shared semantic model; characterization tests | [generators.md](generators.md) |
| Where does service-level metadata live? | Keep; split per service; fold `go:generate` flags in; Go or HCL per service | [discovery-and-placement.md](discovery-and-placement.md) |

A shared semantic model that several generators read is detailed in [shared-implementation.md](shared-implementation.md). Options ruled out on evidence are in [ruled-out.md](ruled-out.md); smaller ideas not tied to a question are in [other-ideas.md](other-ideas.md).

## Works with any choice

- [Generated resource report](resource-report.md): `make resource-info` prints every fact about one resource with its file and line, a view that needs no migration and survives any representation.

## Running examples

Every option file sketches against the same three real resources and refers to them by these names.

**The simple resource (cloudsearch domain).** SDKv2, registration only. The shape of the 42% of resources with no tags, identity, or import ([surface](../findings/surface.md)).

```go
// internal/service/cloudsearch/domain.go
// @SDKResource("aws_cloudsearch_domain", name="Domain")
func resourceDomain() *schema.Resource {
```

**The structured resource (timestreaminfluxdb DB instance).** Framework, with tags, identity, wrapped import, and test generation.

```go
// internal/service/timestreaminfluxdb/db_instance.go
// @FrameworkResource("aws_timestreaminfluxdb_db_instance", name="DB Instance")
// @Tags(identifierAttribute="arn")
// @IdentityAttribute("id")
// @Testing(existsType="github.com/aws/aws-sdk-go-v2/service/timestreaminfluxdb;timestreaminfluxdb.GetDbInstanceOutput")
// @Testing(importIgnore="bucket;username;organization;password", plannableImportAction="Replace")
// @Testing(preIdentityVersion="v6.43.0")
func newDBInstanceResource(_ context.Context) (resource.ResourceWithConfigure, error) {
```

**The exception (elbv2 load balancer with two public names).** One SDKv2 factory registered under both `aws_alb` and `aws_lb`, with tags, ARN identity, and a v6.0 compatibility fix.

```go
// internal/service/elbv2/load_balancer.go
// @SDKResource("aws_alb", name="Load Balancer")
// @SDKResource("aws_lb", name="Load Balancer")
// @Tags(identifierAttribute="arn")
// @ArnIdentity
// @V60SDKv2Fix
// @Testing(existsType="github.com/aws/aws-sdk-go-v2/service/elasticloadbalancingv2/types;awstypes;awstypes.LoadBalancer")
func resourceLoadBalancer() *schema.Resource {
```

The exception is why the public type name is not a unique key. The identifying tuple is (kind, type name), and the one factory emits two registration entries ([registration](../findings/registration.md)). Each resource also appears outside its factory file: in the service's `generate.go`, in `sweep.go`, in `testdata/` fixtures and templates, and in the docs page ([declaration-placement](../../concepts/declaration-placement.md)).
