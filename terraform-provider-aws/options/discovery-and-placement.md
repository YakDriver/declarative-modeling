# Discovery and placement

Two questions that only arise if declarations become typed Go instead of comment markers: how a generator locates a resource's declaration, and which file the declaration sits in. Both are about [where a declaration belongs](../../concepts/declaration-placement.md), not about what it says.

## Finding the declarations

The [representation](representation.md) choice constrains this. A composite literal writes its type at the call site, which syntactic matching can key on. A constructor call does not, so syntactic discovery of constructors means matching known function names, which import aliases and wrappers defeat.

| Option | Good | Bad | Status |
|---|---|---|---|
| Interpret literals statically | byte-identical output possible | reimplements a Go interpreter: walks nested constructors and constants | live |
| Import the package, read the vars | no interpretation step | runs package initialization at generate time (no non-test `init()`, but thousands of `regexache.MustCompile` package vars) | live |
| Match vars by literal type, syntactically | today's parse-only cost (~0.06 s for `ecs`, [generators](../findings/generators.md)); no topology change; no type-error deadlock | misses helper constructors and aliases unless a lint enforces the literal form | [parked](ruled-out.md) |
| Load with types, match by resolved type (`go/packages`) | robust; works for constructors too; scoped load ~1.9 s, under today's ~5 s for `ecs` ([generators](../findings/generators.md)) | needs a typed-syntax load; full `make gen` is ~9 min serial or ~4-6 s and ~2 GB in one load; must tolerate type errors | [parked](ruled-out.md) |
| Hand-written composition root per service | no generator reads registration; ordinary Go; most service lists are small (median 5, [registration](../findings/registration.md)) | registration leaves the factory, so it fails the "declaration sits next to its factory" criterion ([criteria](criteria.md)); a second edit per resource; ec2's list is 288 entries | [parked](ruled-out.md) |
| `init()` registration with blank imports | stdlib precedent (`database/sql`) | global registry and init side effects; the mechanism annotations replaced, rejected in PR #28933 | [rejected](ruled-out.md) |
| Convention, nothing to find | no declaration to locate for most resources | covers existence and naming, not structured metadata | [parked](ruled-out.md) |
| skaff seeds the list once | no generator; list is seeded, not hand-written | the composition root, with its second-location cost | [parked](ruled-out.md) |

The hand-written composition root, for the simple resource (cloudsearch domain):

```go
func (p *servicePackage) SDKResources(ctx context.Context) []*inttypes.ServicePackageSDKResource {
	return []*inttypes.ServicePackageSDKResource{
		{Factory: resourceDomain, TypeName: "aws_cloudsearch_domain", Name: "Domain", Region: inttypes.ResourceRegionDefault()},
	}
}
```

A descriptor variant keeps each entry in its own resource file and reduces the root to a list of calls (`domainDescriptor(), ...`), trading one authored file for one function per resource.

Two problems attach to the type-aware load, neither fatal. A type-aware generator loads a package that contains its own previous output, so deleting or renaming a registration breaks that output; `go/types` continues past type errors ([generators](../findings/generators.md)), so the generator can treat its own output as non-fatal and exclude it. And no option here, including today's, detects a factory that nobody registered; a `go/analysis` check for orphans could be bolted onto any of them.

## Where the declarations live

Go imposes nothing. Every file in `internal/service/kms/` compiles into one package, so this is navigation, diff locality, and merge conflicts, not correctness ([file-organization](../findings/file-organization.md)).

| Option | Good | Bad |
|---|---|---|
| Per-resource, beside the implementation (today's layout) | declaration sits with the symbols it names; adding or deleting a resource touches one file; the conflict surface is per-resource | no single authored place to read a service's whole surface, though `service_package_gen.go` already is that view |
| One file per kind per service (every list declaration in one file) | amortizes imports; a service's list surface reads at once | splits the declaration from the paginator it binds; buys nothing for the 51 of 72 services with 1-3 list resources |
| One file per resource, all kinds together | makes shared schema references visible when resource, data source, and list share one schema | pulls three declarations together while pushing each away from its own implementation |
| One file per service, all declarations | single file to read the service | `sweep.go` is this pattern and reaches 3,475 lines; `ec2/service_package_gen.go` took 241 commits in two years against 14 for `exports.go` ([file-organization](../findings/file-organization.md)). Survivable for a generated file, because conflicts resolve by regenerating; not for an authored one |

The discoverability argument for aggregation is already met by generation. A per-service census does not have to be authored, because `service_package_gen.go` is [derived from the per-resource declarations](../../concepts/derive-before-authoring.md). Authoring an aggregate as well creates the second copy that drifts; [locality points both ways](../../concepts/locality.md), and a generated view gives the per-concern read without a second write surface.

Evidence sits under the per-resource layout beyond inertia. The symbols a list declaration names cluster in the resource file, not the list file: for `aws_kms_alias`, three of four referents live in `alias.go` and only `listAliases` in `alias_list.go`, with ecr identical ([file-organization](../findings/file-organization.md)). Grouping by kind moves the declaration away from all of its referents.

Service-level facts are the exception. Endpoint resolution, client configuration, and service-wide region behavior have no per-resource home and belong in a per-service file under any of these layouts.
