# How facts reach the provider: generate code, or consume a spec

Generation scope and authoring form are independent choices. A declarative surface can be read at generate time, with a generator emitting per-resource Go, or read at runtime, with one generic implementation consuming typed declarations. Most options elsewhere assume the first. The second attacks a different cost: generated volume, not authored surface.

Three positions:

| Option | What would change | Good | Bad |
|---|---|---|---|
| **Generate per-resource Go** (today) | A generator reads declarations and emits Go per resource | Static types and methods per resource; nothing at runtime to debug; emitted Go is readable and reviewable in a diff | Produces volume: 994,564 generated test lines ([generated-tests](../findings/generated-tests.md)) and 20,866 registration lines ([registration](../findings/registration.md)). The generator must read source, so the `ast.go:119` file walk and self-output exclusion apply ([generators](../findings/generators.md)) |
| **Consume a typed spec at runtime** | A typed declaration is passed to one generic implementation (`New(spec)`); little or nothing is generated per resource | Attacks generated volume. One implementation of shared behavior instead of many copies. Nothing reads source. Already in use: list resources embed `framework.ListResourceWithSDKv2Resource` with no codegen ([list-resource-experiment](../findings/list-resource-experiment.md)) | Behavior moves into generics and runtime wiring, harder to read than emitted Go and harder to review in a diff. Debugging crosses from the resource into shared machinery. Generics can't express everything a template can |
| **Split by what the fact feeds** | Consume where a reusable runtime suffices; generate only where static types or methods are genuinely required | Matches where the provider already sits: generation for registration tables, generic runtime for behavior families | Two mechanisms to learn, and a judgment call per family about which side a fact falls on |

These are the "metadata is consumed, not compiled" stance set against generated Go ([philosophies](../../concepts/philosophies.md)).

## The decision is independent of the authored surface

The frequently cited prizes, generating Exists helpers or list resources, are available without changing what a developer authors, because the inputs are already in the code: a finder's signature gives its result type, its parameters, and its client. Treating "generate or consume more" as the same decision as "adopt a spec" credits the authoring format with a benefit the format does not supply.

## What the list-resource experiment showed

Three list resources (`aws_cloudwatch_metric_alarm`, `aws_ecr_repository`, `aws_kms_alias`) were re-expressed as typed declarations consumed by one shared implementation, published as [PR 50577](https://github.com/hashicorp/terraform-provider-aws/pull/50577) and passing their acceptance tests ([list-resource-experiment](../findings/list-resource-experiment.md)). All three were one structural shape: paginate, then flatten each item directly.

- The declarative layer did not relocate the complexity for this shape. None of the predicted failure signals appeared: no custom per-resource knobs, no string-named function references, no generator-specific flags. Every field is a compile-checked Go symbol.
- The metadata was smaller than expected; the flatten signature was the work. Four required fields plus the item type as a type argument, and four candidate facts dissolved. The declaration takes the signature skaff generates, and most existing Shape A flatten functions don't match it yet.
- All four dissolved facts were divergence, not configuration (see [divergence-is-not-configuration](../../concepts/divergence-is-not-configuration.md)): per-item error policy, a cleared-ID check, display-name derivation, and tflog setup differed between the three resources with no apparent intent. Writing the spec straight from the three bodies would have turned all four into knobs.
- Economics: shorter at three resources, counting the shared code.

Not settled: Shape B, the largest group, which lists identifiers and then describes each, was not attempted. Three resources of one shape is a positive signal, not a cleared path.

## The model-shaped trap

A single `ResourceSpec` struct accumulating `TypeName`, `Tags`, `Identity`, `List`, `ExistsType`, `Serialize`, and the rest is the universal metadata surface this investigation identified as the original problem, now with autocomplete. It is **rejected** ([ruled-out](ruled-out.md)): Magic Modules already ran that experiment to about ninety fields with eleven opt-out switches. Any model-shaped option has to separate a small core semantic model from independent per-concern satellites, the criterion "Keeps jobs separate and change contained" ([criteria](criteria.md)), or it reproduces what it replaces. Split authority stays coherent only when each fact keeps exactly one owner (see [intermediate-model](../../concepts/intermediate-model.md) and [spec-or-metadata](../../concepts/spec-or-metadata.md)).
