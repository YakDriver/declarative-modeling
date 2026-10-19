# declarative-modeling

How real systems model resources declaratively: where facts about a resource are written, what reads them, and what that costs.

## What declarative modeling is

A system that manages thousands of similar things (cloud resources, Kubernetes objects, API operations) can't hand-write everything about each one. So it writes some facts down as data: a resource's public name, which attribute identifies it, whether it supports tags, how its tests should run. Something else reads that data and does the work. That's declarative modeling.

The same fact, "tags are addressed by the resource's ARN," in three real forms:

```text
// @Tags(identifierAttribute="arn")                       comment marker (Terraform AWS provider)

"tagging": { "taggable": true,
             "tagProperty": "/properties/Tags" }          external spec (CloudFormation)

Tags: inttypes.ResourceTagsAttribute(names.AttrARN),      typed Go value (the provider's generated registration)
```

Each form answers two questions differently: where the fact is written, and what reads it (a code generator, a shared runtime, or both).

## Why it matters

The answers decide what happens at the 2,000th resource. Get them wrong, and the data quietly becomes the hardest part of the system to change:

- **Mistakes go silent.** Kubernetes `controller-gen` ignores a misspelled marker, and so does the Terraform AWS provider, where a typo'd test opt-out did nothing for years.
- **Vocabulary grows without limit.** Google's Magic Modules validates every value against a schema and still grew to about 90 fields on one struct, because validation catches bad values, not unneeded ones.
- **The authored file isn't the one you debug.** Generate code from a spec, and contributors edit one artifact and debug another, forever.

Get them right, and most facts never need writing at all. Crossplane's Upjet derives what it can from an existing schema and asks people only for the remainder.

## Start here

New to this? Read in this order, about 20 minutes:

1. The [case studies index](case-studies/README.md), for who does what and the one-line lesson from each.
2. [controller-gen](case-studies/controller-gen.md) and [Upjet](case-studies/upjet.md): silent comment markers on one side, a derive-first design in typed Go on the other.
3. [Derive before authoring](concepts/derive-before-authoring.md) and [spec or metadata](concepts/spec-or-metadata.md), the two ideas that do the most work.

## Contents

**Ethos: [Software KonMari](konmari.md).** Keep what serves, give it one home, retire the rest without contempt, and never let the perfect answer block a good step.

- [Case studies](case-studies/README.md): thirteen systems, from Google's Terraform providers to Kubernetes controllers, and what each one teaches.
- [Concepts](concepts/README.md): ideas that hold across systems, like deriving facts before authoring them.
- [Terraform AWS provider](terraform-provider-aws/README.md): the research, options, and plan for changing the provider's annotations.
