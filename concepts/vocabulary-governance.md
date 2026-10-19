# Governing what a shared surface admits is harder than adding to it

A place where many facts about a resource are declared in one spot collects whatever is convenient unless something governs admission. The work that decides the long-term quality of that surface is refusal, not authoring, and refusal is the part that gets no help from tooling.

## Why the surface fills up

A single declaration point that feeds many consumers is an attractor. It is the obvious home for the next fact, and extending it is almost always easier than restructuring around it. Each addition makes local sense when it lands. The sum does not.

Schema validation does not stop this. A typed loader and a validation pass catch malformed values: a verb that is not a real verb, an identity that names a field that does not exist. They say nothing about whether a new field belongs in the model at all. Correctness and restraint are different properties, and the tooling only buys the first.

The cost structure makes it worse. When adding a key meant a person deciding to type it, the friction of that decision was itself a weak filter. When proposing, implementing, and documenting a new key is nearly free, the marginal effort of adding the thirty-fifth knob drops below the effort of noticing that a different abstraction is called for. The scarce resource shifts from authoring effort to review capacity. A representation can then be judged partly on how visible an unwarranted addition is to a reviewer, and how cheap it is to say no. That last point is my judgment, not a measured fact.

## What accretion looks like

[Magic Modules](../case-studies/magic-modules.md) is close to a controlled experiment. Google has generated its Terraform providers from one YAML file per resource for years, with a typed Go loader and a validation pass over every file. That surface still grew to about 90 fields on a single struct, with eleven separate opt-out keys (`exclude_resource`, `exclude_import`, `exclude_delete`, and so on) and keys used exactly once, acknowledged in the code with a `TODO rewrite: 1 instance used`. Validation ran the whole time. It caught bad values, not unwarranted vocabulary.

[controller-gen](../case-studies/controller-gen.md), which reads `// +kubebuilder:` comment markers on Kubernetes Go structs, shows the same drift at the vocabulary level. It offers four separate ways to mark a field optional. The author who ran it in production calls this "simply far too many different ways to achieve something." Four spellings for one concept is the signature of a vocabulary that grew by accretion rather than design, and it teaches users to guess.

The [`@Testing` annotation keys in terraform-provider-aws](../terraform-provider-aws/findings/testing-keys.md) are the same pattern in comment form. An inventory found 54 distinct keys, with 13 of those keys used exactly once. Nobody set out to build a 54-key testing vocabulary in production resource comments. Each key made sense when added, and the surface rewarded extension over restructuring. That is the feedback loop, and nothing in the format resists it.

## The same hazard survives a type system

Replacing an external spec or a comment vocabulary with a typed struct does not remove the attractor. A single model struct holding every concern is the same collector with autocomplete attached. Compile-checking the field names does not decide whether the field should exist. The admission rule has to live somewhere outside the format, because no format enforces it on its own.
