# A declaration belongs next to the symbols it names

Place a declaration by what it points at, not by what kind of declaration it is.

A declaration is a piece of typed code that records facts about something: which function builds a resource, which function finds it, which operation lists it. It names symbols that live in real code. Once a declaration is code rather than a comment, it is bound to those symbols. It will not compile without them, and reading it means jumping to them. Its value is highest when they sit close.

Grouping declarations by category pulls against this. Collecting every list declaration for a service into one file sounds tidy, but each declaration then sits away from the function it builds, the finder it calls, and the helper it uses. In the Terraform AWS provider's [list resource experiment](../terraform-provider-aws/findings/file-organization.md), three of four symbols a list declaration named lived in the resource file, not a separate list file. Category grouping splits each declaration from the paginator and finder it binds.

## Aggregate views should be derived, not authored

The reason people want to group declarations is real: you want to read a whole service's surface at once. But you do not get that by authoring an aggregate. You generate one from the per-resource declarations. Authoring the aggregate as well creates a second copy of facts whose source is elsewhere, and now the two can drift. A generated census is read-only and always current. See [the intermediate model is not the authority](intermediate-model.md).

## Size decides whether per-service aggregation survives

A per-service aggregate file works only while it stays small. The provider has two aggregates that began from the same idea and ended far apart. `generate.go` holds per-service generation directives at a median of 9 lines across 279 services, and it reads fine. `sweep.go` applies the same one-file-per-service pattern to something larger and reaches 3,475 lines at its worst (measured 2026-10-08). The pattern did not fail. The size did.

## Shared implementations move the merge surface

A separate cost appears when a project shifts from generating per-resource code toward one shared implementation driven by authored declarations. The conflict surface moves rather than disappears, and the two surfaces cost differently.

| | Generated files | Authored declarations |
|---|---|---|
| Conflict frequency | High | Proportional to real change |
| Resolution | Rerun the generator; nobody reads the conflict | Manual; someone has to understand both sides |
| Blast radius | The whole generated file | Whatever file the declaration is in |

Generated conflicts are frequent and nearly free. `ec2/service_package_gen.go`, a generated per-service census, took 241 commits in the two years before 2026-10-08, and each conflict resolves by regenerating. Authored conflicts are rarer but genuinely cost something, because a person has to reconcile two edits by hand. This is the strongest argument against aggregating declarations into per-service files, and it has nothing to do with readability. It is about how often two people have to resolve the same file by hand.

[Locality points in two directions](locality.md): the same facts can be read per-resource or per-concern, and a derived view gives the second without a second authored copy.
