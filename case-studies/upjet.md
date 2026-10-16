# Crossplane Upjet

## Summary

Upjet is the framework behind Crossplane's official AWS, Azure, and GCP providers plus "50+ community providers" ([README](https://github.com/crossplane/upjet/blob/main/README.md)). It generates a Crossplane provider from an existing Terraform provider's schema and runs the result on a shared reconciler, so per-resource metadata is authored as typed Go rather than a spec file. provider-upjet-aws generates 1,062 AWS resources this way.

## How it works

Facts come from two places. Upjet "generates as much as it could using the available information in the Terraform resource schema": schema, controller logic, late initialization, sensitive-data handling. The residue it cannot derive (external-name mapping, cross-resource references, extra sensitive fields, late-init behavior, schema overrides) is authored as typed Go, registered per resource:

```go
p.AddResourceConfigurator("aws_s3_bucket", func(r *config.Resource) {
    r.ExternalName = config.NameAsIdentifier
    r.ExternalName.SetIdentifierArgumentFn = func(base map[string]any, externalName string) {
        base["bucket"] = externalName
    }
    r.ExternalName.OmittedFields = []string{
        "bucket",
        "bucket_prefix",
    }
})
```

`config.NameAsIdentifier` and `config.IdentifierFromProvider` are exported package-level `ExternalName` values used as presets: the common case assigns one and stops, an exception overrides individual fields. `SetIdentifierArgumentFn` and the sibling hooks are Go function fields, so behavior binds as real closures. At runtime a generic reconciler drives every generated resource. The config object is read by both the generator (CRDs, controllers) and that shared runtime, the same split as [controller-gen plus controller-runtime](controller-runtime.md).

## What works

- **Derive first, author the residue.** Upjet pulls everything obtainable from the Terraform schema before asking for input, so the authored surface is only what cannot be inferred. This is the same instinct as [Magic Modules'](magic-modules.md) centralized defaults, applied to an upstream authority instead of a local one.
- **Named preset bundles.** The common case is one symbol. `config.NameAsIdentifier` carries sensible defaults (`SetIdentifierArgumentFn` setting `name`, `OmittedFields` of `name`/`name_prefix`); a resource that fits names it and moves on.
- **Behavior as typed closures.** A function field holds the Go closure directly, so there is no string that names a function to be resolved later. The compiler checks it.
- **Generation and shared runtime coexist.** Typed Go is the authority for both. Choosing host-language values does not force a choice between generating code and sharing a runtime.

## What doesn't

- **Field references stay stringly and unchecked.** `OmittedFields` is `[]string`, and the docs cap its reach: "You can omit only the top level fields." Typed Go gives no cheap way to make a *checked* reference to a schema field. Closing that gap needs generated field constants, which is extra machinery, not a property of the language choice. This is the [annotations'](terraform-provider-aws-annotations.md) `identifierAttribute` problem in a different host.
- **Configuration is spread across registration functions**, discoverable only by convention (`config/<group>/config.go`), not from one parsed model.
- **Migration duplication leaks into the authored surface.** Upjet v2 ships both namespaced and legacy cluster-scoped managed resources and uses two `config.Provider` objects. The same resource configuration must be applied to both, and the docs concede "You may need to duplicate common configurations." A migration-era fact became hand-authored duplication.

## Takeaways

- Put derivable facts behind a derivation step, not in the author's hands. The strongest thing Upjet does is shrink the authored surface to the residue an upstream schema cannot express. If an authority already exists, read it; author only what it omits.
- Typed host-language values buy compiler-checked behavior and free preset bundles, but references from a declaration to a schema field stay stringly unless you *also* generate field constants. Budget for that constant generation, or accept an unchecked string.
- Ship the common case as a named value, not as boilerplate every resource repeats. One assignment for the default, field overrides for the exceptions.
- Keep migration-era duplication out of the hand-authored surface. Two provider objects that each need the same config is duplication the author pays for on every resource. If a migration forces fan-out, generate it rather than asking people to copy it.

## Sources

- [Upjet README](https://github.com/crossplane/upjet/blob/main/README.md), read 2026-10-16
- [Configuring a resource](https://github.com/crossplane/upjet/blob/main/docs/configuring-a-resource.md), read 2026-10-16
- [`pkg/config/externalname.go`](https://github.com/crossplane/upjet/blob/main/pkg/config/externalname.go) (preset definitions), read 2026-10-16
- provider-upjet-aws `config/generated.lst` at commit `690b00d`, 1,062 `aws_` entries (`curl -sL raw.githubusercontent.com/crossplane-contrib/provider-upjet-aws/690b00d1d524dee0bb0c5a0d8fea78c699e73d46/config/generated.lst | tr ',' '\n' | grep -c 'aws_'`), read 2026-10-16
