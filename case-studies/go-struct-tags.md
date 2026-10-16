# Go struct tags

## Summary

Go's standard library reads per-field metadata from string literals in struct tags. `encoding/json`, `encoding/xml`, and `database/sql` drivers all consume them at runtime through `reflect.StructTag`. The format is stringly-typed and unchecked, yet it has stayed durable, because each consumer's vocabulary is tiny and `go vet` ships a checker for the grammar.

## How it works

Metadata is authored inline on the field, read at runtime through reflection. The format is a convention, not a type. From `reflect`:

> By convention, tag strings are a concatenation of optionally space-separated key:"value" pairs.

`reflect.StructTag.Get(key)` and `Lookup(key)` split that string. One field can carry several keys (`json`, `xml`, `db`), each owned by a different consumer. `encoding/json` reads only its own key, and its whole vocabulary is a field name plus a few options: `omitempty`, `omitzero`, `string`, and the `-` sentinel.

```go
type User struct {
	Name  string `json:"name"`
	Email string `json:"email,omitempty"`
	Token string `json:"-"`
}
```

Nothing validates the value at compile time. `Get` returns the empty string for a missing key, and the doc is explicit about malformed input:

> If the tag does not have the conventional format, the value returned by Get is unspecified.

## What works

- Tiny, stable vocabulary. A reader holds the whole `json` option set in their head, and it has barely grown in over a decade.
- Co-tenancy. Multiple keys share one field, and each consumer ignores the keys it does not own.
- A checker exists. `go vet`'s structtag pass: "check that struct field tags conform to reflect.StructTag.Get". It validates the `key:"value"` grammar for every key, and flags `json`/`xml` duplicate names, suspicious spaces, and `json`/`xml` tags on unexported fields.

## What doesn't

- The checker guards the grammar, not the option spellings. `encoding/json` tests options with `opts.Contains("omitempty")`, so a misspelled `omitemtpy` compiles, passes vet, and is silently dropped. Weakly-typed metadata needs a linter, and the standard one stops at the envelope.
- No checked references. A tag value is a string, so it cannot name another field or symbol and have that resolved. CloudFormation had to invent JSON pointers to recover this (see [cloudformation-awscc](cloudformation-awscc.md)).
- Values are opaque to refactoring tools. Renaming a Go field does not touch its `json` name.

## Takeaways

- Stringly metadata is fine when the vocabulary is small and stable, so a reader can memorize it and a grammar checker covers the rest.
- The defect is sprawl, not the string. Comment-marker systems that grew hundreds of keys reproduced the pathologies that `json` tags avoid (see [controller-gen](controller-gen.md), [terraform-provider-aws-annotations](terraform-provider-aws-annotations.md)).
- Ship the checker with the format. A format is not a checker, vet is separate code, and even it stops at the grammar.
- When you need checked cross-references or a large vocabulary, strings stop paying. Reach for typed host-language values instead (see [ent](ent.md), [upjet](upjet.md)).

## Sources

- [reflect.StructTag](https://pkg.go.dev/reflect#StructTag), read 2026-10-16
- [encoding/json Marshal](https://pkg.go.dev/encoding/json#Marshal), read 2026-10-16
- [go vet structtag analyzer](https://pkg.go.dev/golang.org/x/tools/go/analysis/passes/structtag), read 2026-10-16
