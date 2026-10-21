# Findings

Measurements of the Terraform AWS provider's annotations, mostly from October 2026. Each file dates its numbers.

- [Annotation inventory](surface.md): 7,025 marker lines of 25 kinds, and individual values recur far more than whole combinations do.
- [`@Testing` keys](testing-keys.md): 51.2% of `@Testing` values are facts the running program can't supply, and `existsType` alone is another 20.5%.
- [Deriving `existsType`](exists-type.md): the type can be derived from the Exists helper 98% of the time, and a wrong derivation is a compile error.
- [Silent failures](silent-failures.md): unknown keys are ignored without a warning, and several keys cross between the test and production paths.
- [Generators](generators.md): 3,063 lines of annotation parsing, and 28 of 29 generator directories have no tests.
- [Registration](registration.md): the type name can be derived for 84.4% of resources, and misses cluster in a few services.
- [Provider contract](provider-contract.md): what the running provider reads from each registration, and registration is the only source of a Framework resource's type name.
- [History](history.md): annotations grew 2.75x since April 2024, and about half of that growth is `@Testing`.
- [Generated tests](generated-tests.md): 994,564 generated test lines, 52% of counted apply steps, with the volume set by templates.
- [List resource experiment](list-resource-experiment.md): typed declarations driving one shared implementation are shorter from the third resource, and the flatten signature is the main obstacle.
- [File organization](file-organization.md): generated per-service files churn the most but resolve conflicts by regenerating, which authored files can't.
