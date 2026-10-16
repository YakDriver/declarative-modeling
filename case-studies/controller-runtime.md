# controller-runtime

## Summary

`sigs.k8s.io/controller-runtime` is the Kubernetes SIG library most Go operators build on: 26,454 known importers on pkg.go.dev (read 2026-10-16). One typed `Reconciler` interface plus a shared `Manager`, cache, and client drive every controller, and per-resource variation lives in Go code, not a metadata language.

## How it works

Resource facts are not authored in a spec. Each controller is ordinary Go that satisfies one interface:

```go
type TypedReconciler[request comparable] interface {
	Reconcile(context.Context, request) (Result, error)
}
type Reconciler = TypedReconciler[Request]
```

A `Manager` owns the shared machinery. Its doc: "Manager initializes shared dependencies such as Caches and Clients, and provides them to Runnables. A Manager is required to create Controllers." The cache, by default, "will watch and list requested objects in all namespaces." The client is split: "the client will use the cache for reads and direct calls for writes." So controllers sharing a kind share one watch stream for it instead of each polling the API server.

The client is typed over `client.Object`, the Go structs for each kind, the same structs [controller-gen](controller-gen.md) turns into CRD YAML. The API shape is typed Go; the runtime behind it is one shared runtime reused across controllers.

## What works

- One small interface. A controller is a `Reconcile` method, and that signature is the entire contract. Nothing about a specific resource leaks into the framework.
- Shared machinery, not copied. Manager, cache, and typed client are written once and injected. The importers reuse the same reconcile loop, workqueue, and caching client rather than each rebuilding them.
- Behavior binds as Go, not strings. Reconcilers are types or `reconcile.Func` closures. No string names a function, so the compiler checks the wiring.
- Level-based by design. Reconcile reads actual cluster state instead of diffing events, so a missed or duplicated event cannot corrupt state: "the reconcile function observes this when reading the cluster state."

## What doesn't

- Cached reads are a sharp default. `GetClient` "may not be a fully 'direct' client -- it may read from a cache." A freshly written object can be absent from the cache when read back, and uncached needs `GetAPIReader`, "used sparingly and only when the cached client does not fit your use case." The sharing that makes it scale also makes staleness a standing gotcha.
- Breaking changes between minor versions. The project stays on a zero major version and "allow[s] breaking changes between minor versions," one per Kubernetes minor release. Consumers absorb churn on the Kubernetes cadence.

## Takeaways

- A shared runtime behind one tiny typed interface scales to tens of thousands of consumers with no metadata language. If per-resource variation is behavior, put it in host-language code against a small interface, not in a spec.
- Separate the typed parts from the stringly parts. The runtime and the Go structs are typed and compile-checked; marker sprawl lives in controller-gen, a different layer. Shipping them from one project does not force them to share a mechanism.
- Keep the interface minimal. `Reconcile(ctx, request) (Result, error)` carries no resource metadata: identity arrives as a name and namespace, and everything else is read at runtime. A narrow contract is what lets one implementation serve many controllers.

## Sources

- [pkg/reconcile/reconcile.go](https://github.com/kubernetes-sigs/controller-runtime/blob/main/pkg/reconcile/reconcile.go) read 2026-10-16
- [pkg/cluster/cluster.go](https://github.com/kubernetes-sigs/controller-runtime/blob/main/pkg/cluster/cluster.go) read 2026-10-16
- [alias.go](https://github.com/kubernetes-sigs/controller-runtime/blob/main/alias.go) read 2026-10-16
- [README.md](https://github.com/kubernetes-sigs/controller-runtime/blob/main/README.md) read 2026-10-16
- [pkg.go.dev importers](https://pkg.go.dev/sigs.k8s.io/controller-runtime?tab=importedby) read 2026-10-16
