# A step has to stand alone

Abandon everything planned after a change. If the system is still better off than before, the change was a step, and its size doesn't matter. If it only pays off once later work lands, it's a down payment, and the real question is whether anyone is good for the rest.

That moves the judgment from direction to self-sufficiency. Direction is cheap, because almost any change points somewhere defensible to the person making it. Self-sufficiency can be checked now, before the plan either happens or doesn't.

The test cuts both ways. It rejects additions justified only by where they lead. And it accepts a small change that leaves things better, even when nobody has the whole answer yet. Holding out for the complete design usually means keeping the current mess.

## Direction without self-sufficiency accretes

Magic Modules' resource definition grew to about 90 fields, eleven separate `exclude_*` switches, and single-use keys, one of them marked `TODO rewrite: 1 instance used`. Each field probably pointed somewhere reasonable when it was added, and schema validation confirmed every value was well formed. What no addition had to answer was whether the whole still made sense ([magic-modules](../case-studies/magic-modules.md)).

`controller-gen` accumulated four different ways to mark a field optional, each presumably reasonable when it arrived ([controller-gen](../case-studies/controller-gen.md)).

## Down payments nobody completes

Upjet v2 has users apply the same resource configuration to two provider objects during a migration, and its docs concede "You may need to duplicate common configurations." The duplication is a down payment on finishing the migration, and until it finishes, every resource pays it ([upjet](../case-studies/upjet.md)).

HashiCorp's Provider Code Specification is a down payment at a larger scale. A versioned intermediate representation between any source of resource facts and any consumer pays off once generators cover behavior, not just schema. Three years after the tech preview, the generators produce schemas and data models, and no component has a release newer than September 2024 ([tfplugingen](../case-studies/tfplugingen.md)). The architecture isn't wrong. The part that shipped doesn't solve the expensive half of the problem on its own.

## Applying it reorders work

In the Terraform AWS provider, converting three list resources to one shared implementation came out at about break-even on lines, paying off only from the fourth resource onward ([list-resource-experiment](../terraform-provider-aws/findings/list-resource-experiment.md)). By itself that's a down payment on converting the rest.

Normalizing the flatten functions those resources call does stand alone. Their return contracts differ, and making them uniform is cleanup worth having even if no shared implementation ever lands (same finding).

So the normalization goes first and ships on its own. The shared implementation follows once its payoff no longer depends on work that may not happen.
