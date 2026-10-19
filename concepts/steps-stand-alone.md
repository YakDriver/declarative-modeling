# A step has to stand alone

Perfection is the enemy of good, and the usual remedy for that makes a different mess. A change that leaves a system better than it found it has done its work, whether or not it reaches the end state anyone sketched. But "this is a step in the right direction" is also how a coherent design becomes a junk drawer, one defensible addition at a time. Both failures are real and they pull opposite ways, so neither "ship progress" nor "wait for the whole answer" is the rule.

The test that separates them: abandon everything planned after this change. Is the system still better off than before? Then it was a step, and its size does not matter. Does it only pay off once later work lands? Then it is a down payment, and the real question is whether anyone is good for the rest.

That reframes the judgment from direction to self-sufficiency. Direction is cheap, because almost any change points somewhere defensible to the person making it. Self-sufficiency is checkable, and it is checkable now rather than after the plan either happens or doesn't.

## Accretion is the failure of direction without self-sufficiency

Magic Modules is the clearest case. Its resource definition grew to roughly 90 fields, eleven separate `exclude_*` switches, single-use keys, and a hand-written escape hatch. Nobody added a bad field. Each one solved a real problem for somebody and pointed in a reasonable direction, and schema validation confirmed every value was well formed. What no addition had to answer was whether the whole still made sense ([magic-modules](../case-studies/magic-modules.md)).

The same shape appears in `controller-gen`, where four different ways to mark a field optional accumulated, each presumably reasonable when it arrived ([controller-gen](../case-studies/controller-gen.md)).

A down payment that nobody completes is the usual mechanism. A field is added because a migration needs it, the migration stalls, and the field becomes permanent while still looking like resource semantics.

## Waiting for the whole answer is the opposite failure

HashiCorp's Provider Code Specification is a sound architecture: a versioned intermediate representation separating any source of resource facts from any consumer of them. It has been tech preview for three years, with no component release in 25 months, while the providers that adopted it generate schemas and hand-write every behavior it does not cover ([tfplugingen](../case-studies/tfplugingen.md)).

The design was not wrong. It was scoped to a boundary (declarative shape, not lifecycle behavior) that left the expensive half of the problem outside, and the expensive half is what adopters needed. A smaller piece that fully solved something would have compounded. The larger design is still waiting.

## Applying it reorders work

The test changes what to do first, not just what to accept. Converting three list resources in the Terraform AWS provider to a shared implementation removed 138 lines and added 120, a net gain of about 15 with break-even near the fourth resource. By itself that does not clearly leave the provider better: it is a down payment on converting the rest.

Normalizing the flatten functions those resources call does stand alone. The return contracts vary three ways across 130 functions, and making them uniform is cleanup worth having even if no shared implementation ever lands ([list-resource-experiment](../terraform-provider-aws/findings/list-resource-experiment.md)).

So the normalization goes first and ships on its own, and the shared implementation follows once its payoff no longer depends on work that may not happen.
