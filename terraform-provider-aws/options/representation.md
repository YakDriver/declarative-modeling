# How structured metadata is represented

Structured metadata means tags, region, identity, import, and versioning: the
facts that sit in markers like `@Tags`, `@IdentityAttribute`, and `@V60SDKv2Fix`
today. The question is what form carries them.

A merged design decision settles the shape for anything that names a factory,
finder, or Go type. [Principle 3](https://github.com/hashicorp/terraform-provider-aws/blob/main/docs/design-decisions/declarative-resource-modeling-principles.md)
requires a compiler-checked Go reference for a Go symbol, never a string, and
requires any proposal for a serialized format carrying such references to argue
against principle 3 directly. Forms that write a Go symbol as a string in a
serialized file are ruled out on that basis; see [ruled-out.md](ruled-out.md).
A serialized format stays correct for reference-free bulk data, which is why
`names_data.hcl` survives. Why a model doesn't cross a process boundary and so
needn't be serialized is in [spec-or-metadata](../../concepts/spec-or-metadata.md).
The options below are the record of what was weighed, not live choices.

## The options

| Option | What would change | Good | Bad | Status |
|---|---|---|---|---|
| Today's annotations | Nothing | Terse; shipped since v4.56.0 | Untyped; silently permissive on typos ([silent-failures](../findings/silent-failures.md)) | Superseded |
| Typed marker catalog | Declared markers, allowed keys, typed targets, one shared parser (controller-gen style) | Fails loud; keeps comments; can generate a marker catalog for docs | Still a comment language; no IDE support; symbol-bearing keys write Go types as strings | Symbol keys [ruled out](ruled-out.md) |
| Shared key list | One shared parser plus a per-marker allowed-key list | Small; fixes silent typos; helps any migration period | Leaves the language as-is | Legacy-hardening |
| Go tool directives | `//tfaws:resource …` with a small grammar; `go/ast` gives argument positions so errors point at the authored line | Go's convention for source-tool comments; excluded from doc text; conversion is a codemod | Still untyped; helps structured metadata only if the grammar grows; symbol-bearing args are strings | Symbol args [ruled out](ruled-out.md) |
| Pass-through Go expressions | Marker arguments are Go expressions copied verbatim into `service_package_gen.go` | Compiler checks the copied code; generator stops interpreting values; terse | Reference lives as comment text, so renames don't carry it and it isn't checked at the authoring site; errors land in generated code without `//line` directives | [Ruled out](ruled-out.md) (principle 3) |
| Authored registration literal | A typed `inttypes` struct literal beside the factory | Typed; completion; compile errors; vocabulary exists in `inttypes` | The simple resource (cloudsearch domain) goes from 1 line to about 6; reviewers read past binding and default syntax | Typed Go |
| Typed constructor | A constructor returning the registration type, variadic options for the rest | Simple case stays near one line; `TypeName` explicit; `inttypes` already uses functional options for identity | Go has no optional arguments, so the structured cases need variadic options across every call site ([registration](../findings/registration.md)) | Typed Go |
| Typed values for structured parts only | Only identity/import authored as typed vars, linked into the generated entry | Typed where interpretation is heaviest; registration stays terse | Two forms coexist; needs a link; tags' placement unclear | Typed Go |
| Sidecar file | Test and structured data in a file beside the resource | Can reference test-only symbols | HCL form names Go as strings; identity keys must move out first | Go form typed; HCL form [ruled out](ruled-out.md) |
| Central HCL file | Resources listed in `names_data.hcl` | Declarative | `factory = "newThingResource"` is an unchecked symbol string; editing the central file needs full `make gen`, breaking the scoped loop | [Ruled out](ruled-out.md) (principle 3) |
| Per-service or per-resource HCL | A schema-validatable HCL file per service or resource | Declarative; per-service gives per-concern locality; prior art in Magic Modules | Roughly 2,679 factory names become unchecked strings; per-resource means about 2,674 files, half holding one fact; per-service means ec2 holds 288 entries. Magic Modules' YAML has nothing to bind to because it *is* the contract ([spec-or-metadata](../../concepts/spec-or-metadata.md)) | [Ruled out](ruled-out.md) (principle 3) |
| Interface methods | `TagsConfig()`, `IdentityConfig()` on the resource | Typed; on the resource; the inner Framework resource exists at wrap time | No SDKv2 equivalent (1,754 SDK registrations); needs a constructed instance, so generators can't read it ([generators](../findings/generators.md)) | Typed, Framework-only |
| Embedded behavior types | `framework.WithTags`-style embedding carrying config | Already used for import and region; readable from AST | Framework-only; embedding can't pass configuration without type parameters or methods | Typed, Framework-only |
| Struct tags | Go-native field metadata | Go-native | Attach to struct fields only, not to functions or package vars | Unusable here |
| Wire-style no-op calls | Valid Go calls existing only for the generator | Real references that rename and find-references see | Package-level state at startup, or a build tag that makes gopls and `go vet` skip the file | [Dead](ruled-out.md) |

## What typed Go has to handle

Every typed option has to carry three-state keys. `common.TriBoolean` exists
because absent and explicit `false` differ, and a plain `bool` can't express
that ([registration](../findings/registration.md)). Identity attributes are
ordered, so the type has to preserve order.

The typed constructor on the exception (elbv2 load balancer) is the case that
decides it. One factory, two public names, tags, ARN identity, and a v6.0
compatibility fix:

```go
var loadBalancerRegistration = inttypes.SDKResource(
	resourceLoadBalancer,
	"aws_lb",
	inttypes.WithAliases("aws_alb"),
	inttypes.WithName("Load Balancer"),
	inttypes.WithTags(names.AttrARN),
	inttypes.WithIdentity(inttypes.RegionalARNIdentity(
		inttypes.WithIdentityDuplicateAttrs(names.AttrID),
		inttypes.WithV6_0SDKv2Fix(),
	)),
	inttypes.WithWrappedImport(),
)
```

The simple resource proves nothing on its own; it stays near one line under
every option.

## Why the serialized forms are out

The ruled-out forms all share one defect: a factory, finder, or type is written
as a string in a file the compiler doesn't check. Rename the function and the
string is silently wrong, the same failure mode as `controller-gen` ignoring a
misspelled marker key and the `tagsTests` typo that sat unreported since March
2023 ([silent-failures](../findings/silent-failures.md)). Attribute-name keys
like `identifierAttribute="arn"` are strings too, which is why principle 3 asks
for `names.Attr*` constants rather than bare literals.

A separate risk cuts across the typed options: a single constructor or literal
that grows a knob per concern becomes the catch-all vocabulary this whole effort
is trying to leave ([vocabulary-governance](../../concepts/vocabulary-governance.md)).
Keeping each concern on its own satellite is what the
"Keeps jobs separate and change contained" criterion asks for in
[criteria.md](criteria.md).
