# Go database/sql driver registration

## Summary

The Go standard library's `database/sql` is used by over 200,000 packages (pkg.go.dev, read 2026-10-16). It has no metadata language at all: a driver calls `sql.Register(name, driver)` from its `init()`, callers pull the driver in with a blank import, and one shared runtime runs over a tiny typed interface. The floor case for "where should metadata live": almost nowhere.

## How it works

A driver registers itself imperatively. `lib/pq`:

```go
func init() {
	sql.Register("postgres", &Driver{})
}
```

`go-sql-driver/mysql` registers `"mysql"` the same way, and documents the consumer side in its package comment:

```go
import _ "github.com/go-sql-driver/mysql"
db, err := sql.Open("mysql", "user:password@/dbname")
```

`Register` stores into a package-level map:

```go
var drivers = make(map[string]driver.Driver)

func Register(name string, driver driver.Driver) {
	...
	drivers[name] = driver
}
```

The registered thing is a minimal typed interface:

```go
type Driver interface {
	Open(name string) (Conn, error)
}
```

Everything else (the connection pool, `Query`, `Exec`, transactions) lives in `database/sql`. Capabilities past `Open` are expressed as further optional interfaces (`Pinger`, `ExecerContext`, `SessionResetter`, and more) that the shared runtime discovers by type assertion, not as declared flags. `lib/pq` asserts them at compile time: `var _ driver.Driver = Driver{}`, `var _ driver.ExecerContext = (*conn)(nil)`.

## What works

No metadata language to learn, drift, or validate. The only authored fact is one name string, and the contract is a Go interface the compiler checks on the driver side.

The core depends on no driver. Registration is a side effect of a blank import, so adding a driver never touches `database/sql`. That is what the import-side `_` buys: wiring without a central list the core must maintain.

Capabilities are typed, not stringly. A driver adds context support by implementing `ExecerContext`; a wrong signature fails to compile. Contrast comment-marker systems where a feature is a string that can be misspelled silently.

## What doesn't

The registry is package-level mutable state. `Register` panics if called twice with the same name or if the driver is nil (`panic("sql: Register called twice for driver " + name)`). The name is an unchecked string, so a collision is a runtime panic, not a compile error.

Registration is invisible at the call site. `sql.Open("mysql", ...)` names the driver in a string; forgetting the blank import is a runtime unknown-driver error, not a build failure.

Package-level state leaks into other packages' APIs. The source marks the map as something that "should be an internal detail, but widely used packages access it using linkname," and keeps a running "hall of shame" of importers that reach in (naming `github.com/instana/go-sensor`). A private global became a de-facto contract the standard library now has to preserve.

Some style guides discourage `init()` for exactly this reason. Uber's guide says "Avoid `init()` where possible," then names "Pluggable hooks, such as `database/sql` dialects" as a legitimate exception. So the canonical "avoid init" guide points at this same pattern as the case where init registration is fine.

## Takeaways

If the only metadata is an identity (a name) plus a behavior contract, you may not need a metadata language. Register a value against a typed interface and let the compiler check the contract. This is the minimal version of typed host-language values; [go-struct-tags](go-struct-tags.md) shows the same "keep the vocabulary tiny" lesson with strings instead.

Express capabilities as optional interfaces discovered by type assertion, not as declared boolean flags. The driver that supports a feature implements it; the runtime asks with a type assertion. The check lives on the authoring side and there is no vocabulary to maintain or misspell.

Pay for the convenience in global state. `init()` plus blank import decouples the core from plugins, but you inherit a mutable singleton: panics on collision, unchecked name strings, no static guarantee the driver is linked in, and a map other packages can reach into. For the opposite choice, an explicit registry preferred over `init()` for the same job, see [terraform-provider-aws-annotations](terraform-provider-aws-annotations.md).

Use this only when the namespace is tiny and the contract is one interface. There is nowhere to put richer per-resource metadata, because the design deliberately has no slot for anything but a name.

## Sources

- [database/sql package](https://pkg.go.dev/database/sql) (read 2026-10-16)
- [database/sql/driver package](https://pkg.go.dev/database/sql/driver) (read 2026-10-16)
- [`sql.go`: `Register`, `drivers` map, linkname comment](https://github.com/golang/go/blob/go1.23.0/src/database/sql/sql.go) (read 2026-10-16)
- [`driver.go`: `Driver` interface](https://github.com/golang/go/blob/go1.23.0/src/database/sql/driver/driver.go) (read 2026-10-16)
- [`lib/pq` `conn.go`: `init()` and compile-time interface asserts](https://github.com/lib/pq/blob/master/conn.go) (read 2026-10-16)
- [`go-sql-driver/mysql` `driver.go`: package doc and `init()`](https://github.com/go-sql-driver/mysql/blob/master/driver.go) (read 2026-10-16)
- [Uber Go Style Guide, "Avoid `init()`"](https://github.com/uber-go/guide/blob/master/style.md) (read 2026-10-16)
