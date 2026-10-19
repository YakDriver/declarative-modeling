# The intermediate model is not the authority

A normalized model that sits between authored facts and the tools that read them is not where those facts get edited. It collects facts whose sources of truth live elsewhere and presents them one way. Reporting a fact through the model does not move ownership of that fact into it.

The confusion is common. Put a normalized representation between inputs and outputs and people read it as "now everyone edits the model." Nothing requires that. Each fact the model carries still has exactly one authoritative source, and the model is a single view every consumer reads the same way.

Mechanism: a fact enters the model from whatever already owns it. Sometimes the owner is code. A function that returns a particular type tells a reader what the result shape is; a frontend extracts that and the model reports it. Sometimes the owner is a written declaration. A line that names an operation is read literally, and the model reports the operation. In the first case the authority is the implementation. In the second it is the declaration. Neither becomes a second authority by being reported.

That is what lets authority be split without becoming ambiguous:

```text
different facts may have different authoritative sources
every individual fact still has exactly one authority
consumers see one normalized view
```

So a fact derived from code and a fact written in a declaration can both feed the same model, and you can still point at one place that owns each. This is hybrid authority done coherently, as opposed to the defect where the same fact is owned in two places with no arbiter (see [spec-or-metadata](spec-or-metadata.md)).

Whether such a model exists is a separate question from how facts are authored and how tools consume them. One in-memory model fed by any frontend separates "how is metadata authored?" from "how do generators consume it?" Its fields divide along how they get filled. Some are references, which any frontend can supply because they point back at a symbol or a declared name. Others are values, which only a frontend holding literal data can supply without interpreting. That split decides which authoring styles can feed the model directly and which would have to guess.

HashiCorp's Terraform provider code generation is this shape in practice. A JSON Schema document it calls the Provider Code Specification sits between a source (an OpenAPI spec, or a hand-written spec) and a Go generator, and the generator is "vendor/tool agnostic" so any source that can emit the spec reuses one back end. The spec is the decoupling layer; the source stays authoritative. Its own lesson is the limit on when this pays off: an intermediate representation between source and consumer earns its keep only when sources or consumers are plural, and with one source and one target you pay for decoupling you will not use ([tfplugingen](../case-studies/tfplugingen.md)).

Pulumi shows the same model justified by consumers rather than sources. One package schema describes a provider and drives SDK generation for six languages. The core schema is language-neutral, and each language generator owns its own extension slice, so a new consumer adds a field there without touching the shared model. For a bridged provider the schema is generated from an upstream provider, which makes it explicitly a projection and not an authority over that provider: behavior stays upstream. Six heterogeneous language targets are the warrant for serializing the model at all ([pulumi](../case-studies/pulumi.md)).

Both cases point the same way. The value of an intermediate model scales with the number of sources or consumers that would otherwise each learn every representation. The normalization is real work, so a model facing one source and one consumer is mostly cost. Judgment: this makes the model a weaker justification on its own than it first looks, because the payoff is a function of how many things sit on either side of it, not of the model being elegant.
