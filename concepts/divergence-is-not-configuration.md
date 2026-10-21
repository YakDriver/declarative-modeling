# A difference between two implementations is not a requirement until someone decided it

When you replace several hand-written implementations with one shared implementation driven by data, every place the originals differ forces a choice. Either the shared code picks one behavior for all of them, or you add a field that selects between behaviors. Adding the field always looks justified, because something really did differ. Do that for every difference and the shared model ends up encoding the historical accidents of the implementations you started from, relabeled as options.

The distinction worth holding: a field is warranted when two cases *need* to differ, not when two cases *happen* to differ. So the question to ask of each difference is whether anyone chose it. If no one did, it is not a requirement, and the shared implementation should pick one answer.

## A worked example

The [list-resource experiment](../terraform-provider-aws/findings/list-resource-experiment.md) is a small case of this. Three resources that each enumerate objects from a cloud API (a metric alarm, a container-registry repository, an encryption-key alias) were rewritten to share one implementation. Collapsing them meant confronting four facts that differed across the three. All four turned out to be differences with no apparent intent behind them:

- On a bad item in the stream, one resource aborted the whole listing; the other two logged the item and continued.
- Only one of the three checked whether an earlier step had cleared the object's ID. The check was correct everywhere; the other two just lacked it.
- All three derived a display name three slightly different ways, and in all three the result equaled the resource ID.
- Identical logging-setup code was repeated in all three.

None of these reads like a decision. They read like three people writing similar code at different times. The shared implementation picked one behavior for each (continue and log on a bad item, check the cleared ID once in the shared loop, default the display name to the ID) and nothing was lost, because there was nothing there to lose. What the per-resource declaration still had to supply was the binding to that resource's own API call and data, not a knob for any of the four differences.

## Why it happens quietly

The failure mode is mechanical. Write the shared model by reading N implementations and parameterizing everything that differs, and you get one field per divergence. Each field looks defensible in isolation. The aggregate is a model that offers N implementations' worth of accidents as configuration, and now every new resource has to answer each knob.

It is the same accretion that produces [sprawling option vocabularies](vocabulary-governance.md), reached from the opposite direction. The usual way a surface bloats is one knob at a time, added as needs arise. Harvesting a shared model from code that already exists bloats it all at once, before anyone has used a single field. The starting point looks principled (every field traces to a real difference in shipping code) which is exactly what makes the result hard to argue with later.

One caution, and this is judgment rather than measurement: telling an accident from a decision is itself a judgment call, and sometimes a difference that looks accidental was load-bearing for a reason not visible in the code. The safe move is not to assume, but to make the resolution loud. Picking one behavior in shared code shows up as a behavior change that review and tests can catch. Promoting the difference to a silent field hides the same question forever. The experiment also covered only one of several shapes these resources take, so it is a sample, not a proof that the pattern always resolves this cleanly.
