# Concepts

Ideas that apply to any system that models resources declaratively.

- [Derive before authoring](derive-before-authoring.md): the cheapest fact is one nobody writes, and derivation is only safe when a wrong result fails loudly.
- [Divergence is not configuration](divergence-is-not-configuration.md): when implementations merge, a difference nobody chose should become one behavior, not a new field.
- [What must survive a redesign](what-must-survive.md): only external contracts and intentional invariants bind a replacement; incidental couplings and defects don't.
- [Locality](locality.md): keeping things together per resource or per concern conflicts only over where a fact is written, and a generated view gives you the other one.
- [Vocabulary governance](vocabulary-governance.md): validation catches bad values, not unneeded fields, so a shared surface needs a rule for refusing additions.
- [The intermediate model is not the authority](intermediate-model.md): a normalized model reports facts owned elsewhere, and it earns its keep only with several sources or consumers.
- [Declaration placement](declaration-placement.md): put a declaration next to the symbols it names, not with others of its kind.
- [Spec or metadata](spec-or-metadata.md): either the declaration is the source of truth or the code is, and mixing the two for one fact is the defect.
- [A step has to stand alone](steps-stand-alone.md): a change that only pays off once later work lands is a down payment, not a step.
- [Philosophies](philosophies.md): five stances on where resource facts live, each with a system that runs it and a cost.
