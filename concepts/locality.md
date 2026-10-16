# Locality points in two directions

"Locality" names two arrangements that pull against each other, and a design can pick only one of them as the place a fact is written.

The word usually means "keep related things together." But there are two ways things relate.

Per-resource locality puts every fact about one thing in one place: its name, its behavior, how it is tested, all beside the thing itself. Open that place and you see everything unusual about the thing without searching.

Per-concern locality puts every instance of one kind of fact together: every naming exception across all resources, or every testing switch, in one file. Open that file and you see how the whole system handles one concern, and which members deviate from the rest.

Both are real conveniences. You work on one thing one day and on one concern the next. The reason you cannot have both is narrow: a fact has one author. The text that defines a thing's name lives either beside the thing or in a file of all names, not both, because two authored copies drift. So the two arrangements compete over where a fact is written, and only there.

Reading is a separate matter. A generated view can present either arrangement from facts authored in the other, so the conflict is smaller than it looks. The distinction worth holding onto: co-location is a write concern (where the author types the fact), discoverability is a read concern (where a reader can see it). Wanting everything about one thing on one screen does not require that everything be authored in one file. A tool can assemble the view.

Distributed authorship with a single assembled view is ordinary. Go's `database/sql` keeps no central list of drivers. Each driver registers itself from its own package's `init`, and the standard library collects them into one map that callers read by name ([database/sql](../case-studies/database-sql.md)). Authority is spread across every driver package; the view is one. Compilers, debuggers, and databases do the same: facts written in many places, unified reports produced on demand.

The Terraform AWS provider shows both halves at once. Each resource authors its registration metadata beside the function that builds it, which is per-resource authority. A generator then collects every resource in a service into one census file that nobody writes by hand, which is the per-concern view, 2,679 entries across the provider ([registration](../terraform-provider-aws/findings/registration.md), [file organization](../terraform-provider-aws/findings/file-organization.md)). The read surface and the write surface are different files, and that works.

The opposite instinct, one authored file that is also meant to be the single view, is where a surface turns into a dumping ground. Magic Modules authors one YAML per resource intended as the single place to read and write that resource. Years of use grew it to about ninety fields on one struct ([magic-modules](../case-studies/magic-modules.md)). A single authored surface attracts whatever is convenient (see [vocabulary governance](vocabulary-governance.md)). A generated view attracts nothing, because no one writes to it.

The formulation that resolves the conflict:

```text
one read surface, many appropriate write surfaces
```

This does not dismiss the instinct behind per-resource locality. Someone who wants to open one thing and know everything odd about it is asking for something legitimate. The point is that a generated view satisfies that request, so the request does not force single authorship. If no such view exists, then the single authored surface really is the only thing that meets the need, and defending it is reasonable. The fix is to build the view, not to argue down the need.
