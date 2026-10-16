Not everything a system does today is a requirement, so before redesigning it, sort current behavior into four classes and keep only the two that bind.

A working system behaves the way it does for different reasons, and those reasons are not equally binding on a replacement. Four classes separate them:

- **External contract.** Someone outside the system depends on it. Changing it breaks them or forces a migration. A public identifier that users write in their own files is a contract: rename it and their references stop resolving.
- **Intentional invariant.** Internal, but deliberately relied on. Changing it is a coordinated internal edit, not a user-visible break. A uniqueness rule enforced at startup is an invariant: the code assumes it everywhere, and a replacement has to keep enforcing it.
- **Incidental coupling.** It works this way, but nobody chose it. Two things ended up sharing a value, or one derived from another, as a side effect of how the code was written. Breaking it is mechanical and can be large, but it costs no one outside.
- **Defect or debt.** Wrong today. A replacement should fix it, not reproduce it.

Only the first two constrain a new design. The cost of changing something is a separate question from whether it binds: an incidental coupling can be expensive to untangle and still not be a requirement.

The classes are easy to confuse because all four look the same from inside running code. A concrete split, from one code generator that attaches metadata to source files ([provider-contract](../terraform-provider-aws/findings/provider-contract.md)):

- The public resource type name is an external contract. It keys the runtime lookup and is the only source of some type names, and users depend on its exact spelling.
- Rejecting duplicate type names at startup is an intentional invariant.
- A resource's internal "friendly name" doubling as a filesystem path for test fixtures is incidental coupling. The same string names 685 fixture directories holding 4,063 files, so changing it moves directories, but that was never a decision anyone made.
- A misspelled key that no reader consumes is a defect: `tagsTests` where the consumer looks for `tagsTest`, ignored with no warning ([silent-failures](../terraform-provider-aws/findings/silent-failures.md)).

Sorting this way is itself judgment, and the hard cases are incidental couplings that look like contracts because something would break if you changed them. The test is whether anyone decided it. This is the same question that separates [divergence from configuration](divergence-is-not-configuration.md): a difference that no one chose is not a requirement.

How you check that a redesign preserved what must survive depends on what you are checking.

**Byte-identical output** compares the generated artifact against a committed copy. It is free and total, and it is exactly right when the point of a change is to re-source the same generator without changing results. But it freezes every detail it captures, including the incidental ones, so the moment you intend to generate something different it reports the intended change as a failure.

**Resolved-model equivalence** compares the meaning instead of the bytes. Magic Modules shows why the two come apart: a custom serializer strips any field still at its default, so the authored file can shrink while the parsed resource model is unchanged ([magic-modules](../case-studies/magic-modules.md)). The bytes differ; the resolved model does not. The reverse also happens. The CloudFormation-driven provider makes every optional property Computed, which is a real semantic change you would want a model comparison to catch rather than a diff to hide ([cloudformation-awscc](../case-studies/cloudformation-awscc.md)).

A model comparison is only as honest as the facts it asserts. Assert the external contracts and intentional invariants, and it protects what must survive. Assert the incidental couplings too, and it freezes them in place, turning accidents into requirements the next redesign has to honor.
