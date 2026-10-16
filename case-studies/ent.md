# ent

## Summary

ent is an entity framework for Go whose schemas are ordinary Go code and whose API is generated from them: "100% statically typed and explicit API using code generation." It was inspired by an internal Meta (Facebook) framework, open sourced in 2019, and joined the Linux Foundation in September 2021. It is the cleanest public proof that declarative Go, held as the single authority, can drive a large generated surface, and that it does so by choosing a generator over a shared runtime.

## How it works

Resource facts live in host-language Go, not an external file or comment markers. A schema is a struct that embeds `ent.Schema` and returns typed field and edge declarations from methods:

```go
type User struct {
	ent.Schema
}

func (User) Fields() []ent.Field {
	return []ent.Field{
		field.Int("age").Positive(),
		field.String("name").Default("unknown"),
	}
}

func (User) Edges() []ent.Edge {
	return []ent.Edge{
		edge.To("cars", Car.Type),
	}
}
```

`go generate ./ent` reads these schemas and writes a typed client. For the two-entity quick start that output is `client.go`, `mutation.go`, a per-entity package (`user/user.go`, `user/where.go`), and `user_query.go`, `user_create.go`, `user_update.go`, `user_delete.go`, among others. Querying is then type-checked: `client.User.Query().Where(user.Name("a8m")).Only(ctx)`.

The documented principles are "Define schema as a programmatic Go code" and "Static typing based on code generation." The consumer is a generator. There is no shared runtime interface that every schema implements at execution time; the behavior ships as generated per-entity code.

## What works

The authority is real Go, so it composes, refactors, and type-checks before anything is generated. An edge names another schema by symbol (`Car.Type`), not by string, so a reference to a missing entity fails to compile. That is a checked reference obtained for free from the host language, the thing CloudFormation had to rebuild with JSON pointers (see [cloudformation-awscc](cloudformation-awscc.md)) and the thing comment markers lose (see [controller-gen](controller-gen.md)).

The generated surface is typed end to end. Callers get methods like `SetAge` and `SetName` rather than an `interface{}` or map-shaped API, so field typos surface at compile time in consumer code, not just in the schema.

Scale is public. ent ran inside Facebook before open-sourcing, is now under Linux Foundation governance, and is developed and maintained by the Atlas team. A framework built for "large data-models" with many entity types is evidence the pattern holds past toy size.

## What doesn't

The generated surface is large: roughly a dozen files plus a package per entity, from a few lines of schema. I think the practical cost is that the artifact you read while debugging a query is generated code, not the schema you authored, the same split that external-spec systems have between YAML and generated Go (see [magic-modules](magic-modules.md)).

Any schema change means regenerate and rebuild before the typed client reflects it. That is a faster loop than a cross-repo spec pipeline, because the schema and its generator live in the same module, but it is still a generation step, not live interpretation.

ent models database entities, fields, edges, and indexes. It is not a general resource-lifecycle system; drift, diff suppression, waiters, and import have no analog here. Reading it as proof that "Go schemas can express anything" would overreach what it actually demonstrates.

## Takeaways

- Declarative Go as the single authority scales to a large generated surface. If the goal is type-checked, refactorable resource facts, host-language values deliver it without an external format (contrast [go-struct-tags](go-struct-tags.md), where stringly tags stay cheap only because the vocabulary is tiny).
- Typed declaration does not imply a shared runtime. ent is firmly in the typed-host-language family yet consumes its schemas with a generator, not a runtime interface. Choosing typed Go and choosing generation are independent decisions; [upjet](upjet.md) pairs typed Go config with both a generator and a shared runtime, ent takes only the generator.
- References between declarations should be host-language symbols, not strings. `edge.To("cars", Car.Type)` fails to compile against a missing target. Design the authority so a wrong reference cannot be written, rather than adding a validator to catch it later.
- Budget for the generated surface. The cost of this design is not expressiveness, it is that the code you debug is generated and must be regenerated on every schema change. That trade is worth naming up front.

## Sources

- [ent/ent README](https://github.com/ent/ent/blob/master/README.md), read 2026-10-16
- [ent Quick Introduction](https://entgo.io/docs/getting-started/), read 2026-10-16
- [Ent Joins the Linux Foundation (entgo.io)](https://entgo.io/blog/2021/09/01/ent-joins-the-linux-foundation), read 2026-10-16
- [Ent Joins the Linux Foundation (linuxfoundation.org)](https://www.linuxfoundation.org/blog/blog/ent-joins-the-linux-foundation), read 2026-10-16
