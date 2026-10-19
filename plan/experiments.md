# Experiments

Experiments worth running, and the results already in. Each says the question, the method, and what result would change the plan. Results already obtained link to the finding that records them. Pieces and parked items are in [README](README.md).

## Still worth running

**Does the shared list-resource implementation scale past Shape A?**
Question: the spike converted three Shape A resources (paginate and flatten each item); does the four-field typed declaration hold for Shape B (list identifiers, then describe each), the larger population at 65 files?
Method: convert one Shape B resource, for example `aws_sns_topic_policy`, and test against AWS.
What would change: whether piece 3's shared implementation extends beyond the ~53 Shape A files or stops there. Shape A was positive and eliminated nothing ([list-resource-experiment](../terraform-provider-aws/findings/list-resource-experiment.md)).

**Does the `existsType` type-argument mechanism generalize?**
Question: does replacing the string-named type with a type argument work beyond two resources, across the 492 occurrences?
Method: piece 4 on comprehend's two resources; a wrong type is a compile error, so compiling verifies it.
What would change: if it generalizes, the largest single key can be removed; if not, the recoverable share of the surface drops sharply. Derivation routes already measured: the hand-written Exists helper resolves about 98%, file-local finders about 74% ([exists-type](../terraform-provider-aws/findings/exists-type.md)).

**Why do 121 services skip `tagstests`?**
Question: deliberate, omission, or missing fixtures?
Method: walk each service's `generate.go` and `testdata/` templates; a sample of 30 suffices if the full set runs long.
What would change: the liveness checker (piece 5) must treat a fixture-less service differently from an inert key, and the answer decides whether a per-service or per-resource test switch is the right shape ([testing-keys](../terraform-provider-aws/findings/testing-keys.md)).

**What does a full report-only scan find?**
Question: beyond the known `tagsTests` typo and the inert opt-out lines, how many wrong or inert keys exist?
Method: piece 5's checker across `internal/service`.
What would change: a small, clean result makes enforcement cheap to turn on; a noisy one means classification work before enforcement. Known already: the one live typo, and test-generation keys that gate `make gen` while appearing in no generated file ([silent-failures](../terraform-provider-aws/findings/silent-failures.md)).

## Parked

Each returns with its parked piece in [README](README.md).

- **Derive the public type name with a loud-failing rule.** Returns with registration redesign. A wrong type name is a silent breaking change to a public API, unlike `existsType` where a wrong value fails to compile ([exists-type](../terraform-provider-aws/findings/exists-type.md)).
- **Native `Metadata` on two Framework resources.** Returns if the team decides uniformity across plugin frameworks is not required. It doubles as the experiment for that judgment call.
- **Maintainer review of one resource in several authored forms.** Returns if authored-literal density becomes the blocking question. It is a poll, not a measurement.
- **Factory discovery accuracy** and **directive error locality.** Return with registration redesign.
- **Typed loading cost at full `make gen` scale.** Already probed: per-package typed loading across 274 packages is roughly 9 minutes, warm cache, one machine ([generators](../terraform-provider-aws/findings/generators.md)). Rerun only if a redesign depends on it.

## Cut

Deriving the friendly `Name` (a wrong one silently relocates 685 fixture directories) and asking the constructed object at startup about Import, Region, and Tags presence both feed registration, so they are cut rather than parked (see [README](README.md)).
