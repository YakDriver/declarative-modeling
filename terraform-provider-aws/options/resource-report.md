# Generated resource report (`make resource-info`)

A read-only projection of everything known about one resource, with the file and line each fact came from. It works with any choice in the other option files. Nothing about it depends on how facts are authored.

```text
$ make resource-info RESOURCE=aws_ecs_service
aws_ecs_service  (SDKResource)
  Name        "Service"            ecs/service.go:40
  Tags        identifierAttribute  ecs/service.go:41
  Identity    (none)
  existsType  ecs.Service          ecs/service_test.go:28
```

A generator reads what's already parsed and prints it. It writes nothing anyone edits.

## Why it's non-exclusive

The report is a view, not an authority. Wherever a fact is authored today (a marker on the factory, `generate.go`, `names_data.hcl`, a test file) and wherever it moves later, the report reads it from there. So it can ship now, keep working through any migration, and outlive whichever representation wins. A per-concern version (every resource's tag identifier, every test opt-out in a service) is the same data sorted differently.

It meets the real need behind one authored surface per resource: seeing all of a resource's knobs in one place. That surface is ruled out as an authority ([ruled-out](ruled-out.md)), because a [locality](../../concepts/locality.md) conflict is only over where a fact is written. Reading can be arranged either way.

## Good

- No migration and no change of authority, so it's fully reversible.
- It serves "discoverable per resource and per concern" ([criteria](criteria.md)) without trading away co-location.
- It's the first consumer of a normalized model ([intermediate model](../../concepts/intermediate-model.md)), so it tests that idea on one concern at a time.
- Its gaps are the inventory. A fact it can't print has no shared model yet, and a fact whose file and line it can't name has no single authority. That list is the work plan, generated rather than argued.

## Bad

- It's only as complete as what it reads. Registration, tags, and identity are already parsed in one place: `servicepackage` was refactored in September 2026 to pre-parse annotations into a list (commit `cf5851077a8`), and identity facts go through a shared layer ([generators](../findings/generators.md)). `@Testing` keys, `generate.go` wiring, and service metadata would each need their own reader.
- Another generator to maintain, in a directory tree where 28 of 29 generator directories have no tests ([generators](../findings/generators.md)). It needs characterization tests like the rest.
