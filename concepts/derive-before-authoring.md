# Derive before authoring

Classify each fact about a resource before you write it, by what role it plays and where its value comes from. The classification tells you whether anyone needs to write it at all, and the cheapest fact is the one nobody writes.

Two independent axes.

**Role** is what the fact means:

- A *switch* is a policy decision nothing else prescribes, like whether a resource gets a generated test.
- A *fact* is a property that is simply true of the resource, like its public type name or which attribute holds its identity.
- A *binding* is an association between two things, like a type name pointing at the function that builds it.

**Source** is how the value gets supplied:

- *Authored*: a person writes it. It gets reviewed, and it can be mistyped.
- *Defaulted*: policy supplies a value unless someone overrides it, so only the exceptions are written.
- *Derived*: it follows logically from another value that is already authoritative. Writing it anyway creates a second copy that can drift.
- *Inferred by convention*: it probably follows from naming or structure, with exceptions, so it needs overrides and a rule that refuses rather than guesses.

The axes don't line up. A switch can be defaulted, a fact can be inferred, a binding can be authored or inferred. A fact is *irreducible* only when authoring is the single option available, like the public name of a resource whose name follows no pattern.

Role and source together tell you the cheapest way to get each fact. A value determined by other values is a restatement with a failure mode. When behavior can attach itself because the facts that imply it are already present, there is no key to write, no documentation for the key, no misspelling, and nothing to review. That is the best case: no lever at all.

Magic Modules shows defaulting done well. Its generator fills in values like `CreateVerb: POST`, then omits any field still at its default when it writes the file back, so authored specs shrink as defaults land instead of growing (see [magic-modules](../case-studies/magic-modules.md)).

Derivation has a sharp edge: it is only safe when a wrong result fails loudly. A derivation that guesses wrong in silence is worse than a value a person wrote, because nobody sees the mistake. controller-gen, which turns annotated Go structs into Kubernetes schemas, ignores any marker it does not recognize, so writing `:enum` instead of `:Enum` does nothing and says nothing; the misspelling fails open (see [controller-gen](../case-studies/controller-gen.md)). The AWS provider has the same shape: `@Testing(existsType=...)` writes a resource's Go type as a string 502 times, duplicating a type the code already returns (see [terraform-provider-aws annotations](../case-studies/terraform-provider-aws-annotations.md)), and a one-character typo in a different key sat unread for years (see [silent failures](../terraform-provider-aws/findings/silent-failures.md)).

Reducing authored volume and making behavior automatic are different moves. Deriving what is knowable cuts how much gets written; making behavior automatic cuts how many decisions get made. Both help, and both can be pushed past the point where a reader can still tell what a resource does from what was written about it. That is a judgment, not a measurement. When a fact and its derivation are the same thing with no intent between them, the derivation wins; see [divergence is not configuration](divergence-is-not-configuration.md).
