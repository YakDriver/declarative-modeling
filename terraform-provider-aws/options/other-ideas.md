# Other ideas

Ideas raised that don't fit the representation, discovery, or test-fact options. A re-keyed fixture directory and checkable attribute references work with any authoring form, like the [generated resource report](resource-report.md). The rest are inference sources and parser variants, most carrying a known defect.

## Fixture directory keyed on filename or type name

Generated tag and identity tests point at `testdata/{Name}/`, so the friendly name `Name` is a filesystem key, not just a diagnostic label. A derived `Name` that guesses wrong relocates fixture directories and points tests at a path that doesn't exist (see [divergence-is-not-configuration](../../concepts/divergence-is-not-configuration.md)). Re-keying the fixture path on the source filename or the public type name decouples `Name` from the 685 checked-in directories ([provider-contract](../findings/provider-contract.md)), so `Name` could then be derived freely.

The three test templates (`tagstests`, `identitytests`) would emit `testdata/{sourceName}/` or `testdata/{typeName}/`, and the 4,063 `.tf` files ([generated-tests](../findings/generated-tests.md)) move once to match.

Good: removes the one reason `Name` must stay authored for most resources. Bad: a one-time move of 4,063 files plus template changes, and the type name isn't unique (a resource and its data source share one), so the filename key is the safer choice. Parked (see [names](names.md)).

## Checkable attribute references

CloudFormation's `tagging.tagProperty` is a JSON pointer such as `/properties/Tags`, resolved against the resource's declared schema, so a validator confirms the target exists (see [CloudFormation case study](../../case-studies/cloudformation-awscc.md)). The provider's attribute-naming keys (`identifierAttribute` and the identity and import attribute keys) are unchecked strings. Resolving them against the resource's schema at generate time would catch a misspelled attribute without changing the syntax, closing part of the fail-early gap ([silent-failures](../findings/silent-failures.md)). Independent of the representation question, and compatible with keeping today's markers.

## The rest

| Idea | Good | Bad | Status |
|---|---|---|---|
| CloudFormation schemas (tagging, primary identifier) as an inference source | External authority already exists | Not 1:1 with Terraform attributes | |
| Doc-comment conventions without the `@` marker | Reads naturally | Same parser problem, worse syntax | |
| Per-resource `//go:generate` carrying flags | Uses an existing mechanism | Moves the language into a flag DSL | |
| Hand-written provider-wide registry package | Explicit | Central merge-conflict file, the thing annotations were built to avoid | |
| Schema-first factory generation (factories from a spec) | Removes far more boilerplate | Scope excludes registration, test policy, identity, and lifecycle; resource code is hand-written by design (see [spec-or-metadata](../../concepts/spec-or-metadata.md)) | rejected ([ruled-out](ruled-out.md)) |
| Per-concern service files (all naming exceptions, or all testing policy, for a service) | The per-concern locality several maintainers asked for | Resource configuration no longer in one place; new artifacts | |
| External schema language (CUE, protobuf-style IDL) | Typed source with defaults and validation | Go symbols become strings or need a bridge, the same trade as the HCL forms (see [representation](representation.md)) | rejected ([ruled-out](ruled-out.md)) |
| Reflection-based discovery | No declarations at all | Go reflection can't enumerate functions nothing references | |
| Per-service Go `plugin` packages | Dynamic loading | No Windows support; build and deployment complexity | |
| Generated per-resource registration file instead of one per service | Generated diff sits beside the resource it describes | 2,679 more generated files ([registration](../findings/registration.md)); no change to the authored side | |
