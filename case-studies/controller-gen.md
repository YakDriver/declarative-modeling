# controller-gen

## Summary

Thousands of Kubernetes projects author API types as Go structs and attach metadata with `// +kubebuilder:` comment markers; controller-gen reads the markers and generates CRD YAML. It is the usual example of "declarative Go," but it is two systems: typed structs that work, and a stringly-typed marker layer that reproduces the failures of any comment-driven metadata. The shared-runtime half is [controller-runtime](controller-runtime.md).

## How it works

Resource shape lives in Go structs. Validation, defaulting, and output metadata live in marker comments on the fields. controller-gen is "a tool that turns Go structs with comments-based markers into Kubernetes CRD manifests." Markers are "single-line comments that start with a plus, followed by a marker name," optionally with configuration.

```go
type CarSpec struct {
    //+kubebuilder:validation:Enum=BMW;Porsche;McLaren
    //+required
    Brand string `json:"brand"`
}
```

The struct is the authority for shape. The markers are a separate, string-parsed vocabulary layered on top.

## What works

The struct half is genuine typed declaration. Field names, types, and nesting are Go, so they compose, refactor, and compile-check. That is the part everyone means when they call the system clean.

Scale is real: "at least 7,000 Kubernetes Custom Resource Definitions in the open source corpus," most generated this way.

## What doesn't

The marker layer carries the defects of stringly-typed metadata, documented by Ahmet Alp Balkan from running it in production.

Unrecognized markers are silently ignored. controller-gen "does not validate the markers it does not recognize," so `//+kubebuilder:validation:enum=...` (lowercase) does nothing. The author links a code search and notes you would be "one of the dozens of developers that thought `controller-gen` would've complained if you misspelled `:Enum` as `:enum`." Metadata that is wrong but syntactically plausible fails open.

Too many ways to say one thing. Four separate ways mark a field optional (`omitempty`, `//+optional`, `//+kubebuilder:validation:Optional`, and a package-level default). The author calls this "simply far too many different ways to achieve something."

The vocabulary was incomplete on a basic axis for years. "Up until controller-tools v0.16 (released last month) **it was not possible** to reliably mark a field as *required*," because `omitempty` silently turned a `+required` field optional.

Defaults sometimes must be written twice, once on the field and once on the parent struct, which the author calls "potentially a maintenance nightmare."

Expressiveness ceiling. [controller-tools#461](https://github.com/kubernetes-sigs/controller-tools/issues/461), "Support more complex validations (oneOf/anyOf/allOf/etc)," stayed open from July 2020 to August 2026 because those JSON Schema constraints had no marker form. It closed not by adding native `oneOf` but by shipping CEL-backed `AtMostOneOf`/`ExactlyOneOf` markers. For most of its life the markers could not express a common validation shape, and the fix routed through a different mechanism.

The author's own conclusion: "Just like any weakly-typed system, `controller-gen` ideally should be accompanied by a more robust static analysis tool or linter."

## Takeaways

Split the authority the way controller-gen accidentally did, and be honest about which half is which. Shape in the host language is typed and refactorable. Metadata in comment strings is not, and a well-resourced Kubernetes project hit silent misspellings, redundant vocabulary, and a missing `required` for years. If metadata must live in markers, the checker is separate work that has to be funded; the format alone will fail open. Prefer putting metadata where the compiler already sees it, in typed values, over inventing a comment vocabulary you then owe a linter.

Watch for one concept with several spellings. Four ways to say "optional" is a smell that the vocabulary grew by accretion, not design. Collapse synonyms before they teach users to guess.

An expressiveness ceiling in a marker language is not hypothetical, and climbing out of it is slow. Six years to resolve one validation shape, resolved by bolting on an expression language rather than extending the markers, is the cost of choosing a vocabulary too narrow for the schema underneath it. If the target format is richer than your markers, that gap becomes permanent pressure.

## Sources

- [CRD generation pitfalls](https://ahmet.im/blog/crd-generation-pitfalls/), Ahmet Alp Balkan (read 2026-10-16)
- [Kubebuilder book, markers for config/code generation](https://book.kubebuilder.io/reference/markers) (read 2026-10-16)
- [controller-tools#461, oneOf/anyOf/allOf support](https://github.com/kubernetes-sigs/controller-tools/issues/461) (read 2026-10-16)
