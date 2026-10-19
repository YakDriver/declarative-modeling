# Making declarations fail loud and checking what they mean

Two separate questions. First, how do wrong keys and malformed lines stop being silent. Second, where the checks that need more than one value run. Both serve the one hard constraint the status quo violates, [criteria.md](criteria.md)'s "fails early, locally, and never inertly": a wrong key must reach a human, and an authored item with no active consumer must be reported. Today a wrong key reaches no one: `@Testing(tagsTests=false)` is a typo for `tagsTest` and is dropped without a word ([silent-failures](../findings/silent-failures.md)).

## Making unknown keys fail loud

This is the legacy-syntax half: catch typos and malformed markers while the comment language still exists, independent of whatever replaces it.

| Option | What changes | Good | Bad |
|---|---|---|---|
| Each consumer errors on keys it didn't read | Each generator rejects keys it doesn't recognize | Minimal code | Generators read different subsets of the same marker, so valid keys get flagged |
| Shared per-marker allowed-key list | One list of known keys per marker, consulted by every consumer | Correct; small | One more list to maintain |
| Full key-definition table | Reuse the complete key schema a typed replacement would build | Complete | More than a legacy layer needs if the language is going away |
| Error on marker-looking lines that fail the regex | Treat a near-miss marker as an error, not a non-marker | Catches malformed syntax | Fallout across services; some typos may be load-bearing |
| Report-only first | A command that lists unknown keys and malformed markers, fixing nothing | Sizes the fallout | Doesn't fix anything by itself |
| Analyzer in `.ci/providerlint` | A `go/analysis` pass flagging unknown keys in the editor | Errors at the annotation in the editor; suggested fixes for typos | Duplicates the generator's key knowledge unless both share the key list |

The shared key list lives once, in `internal/generate/common`, so the generator and an analyzer read the same source and can't drift ("one definition, one authority"):

```go
var markerKeys = map[string][]string{ // (new)
	"Tags":    {"identifierAttribute", "resourceType"},
	"Testing": {"existsType", "importIgnore", "preIdentityVersion", "tagsTest" /* … all 54 */},
	// …
}
```

Report-only sizes the blast radius before anything is made fatal:

```text
$ go run ./internal/generate/annotationcheck   # (new)
elasticache/reserved_cache_node.go:37: @Testing: unknown key "tagsTests"
1 unknown key, 0 malformed markers, 2,670 files
```

An unknown-key check clears only the "no silent error" part of the threshold. It catches `tagsTests`, but not a correctly spelled key in a service that never runs the generator consuming it. That second half (no inert configuration) needs a cross-direction check, which lands in the next question.

## Where semantic validation runs

Shape-and-value checks can live in several places, and they differ in how early they fire and in how much resource knowledge the checker has to hold.

| Option | What changes | Good | Bad |
|---|---|---|---|
| In the generator (today, ~40 checks) | Keep checks inside the generators | Fails at generate time | Generator holds resource semantics, against "generators don't know individual resources" |
| `Validate()` on registration types | Each registration type checks its own rules; `TestProviderInit` calls it | Types own their rules; CI always runs it | Needs care so it doesn't become a dumping ground |
| Collection-level validation | Check across registrations: duplicates, cross-registration consistency | Catches what single values can't; duplicates must key on (kind, type name) because type names are shared across kinds ([provider-contract](../findings/provider-contract.md)) | Separate home to keep straight |
| Provider startup | Rely on the running provider, which already rejects duplicates and import inconsistencies | Already exists | Fails at runtime, later than CI |
| `go/analysis` pass in `.ci/providerlint` | A static pass reporting at the declaration | Runs in CI and editors; reports at the declaration; providerlint already runs several passes | Static only; can't check values computed at runtime |
| Relational checks over one parsed model | Accumulate cross-field errors over a shared model (identity entries must name a declared property; one flag implies another's cardinality), the Magic Modules pattern ([magic-modules](../../case-studies/magic-modules.md)) | Catches the class no single-value check can: a reference to something that doesn't exist, or two keys that contradict | Requires the three generators to share one model instead of each walking the comments alone ([generators](../findings/generators.md)); today's ~40 checks live in `servicepackage` only, so tag-test and identity-test keys get no relational checking |

A per-type `Validate()` keeps the rule next to the type and runs in CI without a separate tool:

```go
func (r ServicePackageSDKResource) Validate() error { // (new)
	if r.TypeName == "" {
		return errors.New("TypeName is required")
	}
	// registration-local checks only
	return nil
}

// TestProviderInit, after building the provider
for _, sp := range servicePackages(ctx) {
	for _, r := range sp.SDKResources(ctx) {
		if err := r.Validate(); err != nil {
			t.Errorf("%s %s: %s", sp.ServicePackageName(), r.TypeName, err)
		}
	}
}
```

The relational option is the only one that catches a reference to something that doesn't exist or two keys that contradict, and it's the one that costs a shared model. That model is a view, not a new place to edit facts ([intermediate-model](../../concepts/intermediate-model.md)); whether it exists at all is the generator-invocation question ([generators.md](generators.md)). The places stack: editor, compiler, `make gen`, CI, startup. Earlier catches more. The threshold only asks that an error reach a human somewhere short of "never".
