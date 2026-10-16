# HashiCorp Terraform provider code generation

## Summary

HashiCorp's own answer to spec-driven providers: a JSON Schema intermediate representation (the Provider Code Specification) sits between a source of truth and generated Go, with `tfplugingen-openapi` feeding it and `tfplugingen-framework` consuming it. It generates schema and data models, not CRUD, and has stayed in tech preview since October 2023. The most relevant in-house datapoint for anyone weighing an external-spec-to-Go pipeline, because it shows where that pipeline stops.

## How it works

Three separate repositories form a pipeline:

| Stage | Tool / artifact | Role |
|---|---|---|
| Source | OpenAPI 3.x spec plus a YAML generator config | authored or vendor-supplied |
| Transform | `tfplugingen-openapi` | OpenAPI to spec |
| IR | Provider Code Specification (JSON Schema) | the decoupling layer |
| Generate | `tfplugingen-framework` | spec to Plugin Framework Go |

The Provider Code Specification is "a versioned interface which is defined with a JSON schema, and has associated Go language bindings." The generator design is "vendor/tool agnostic," so any source that can emit the spec can reuse one Go generator.

The OpenAPI stage does not derive everything. "A developer will need to configure which API operations (GET, POST, etc.) and components map to a given Terraform resource, data source, or provider. A YAML file (generator config) is used to define these mappings."

The framework stage has two commands. `generate` produces files suffixed `_gen.go` and marked "DO NOT EDIT." `scaffold` produces starter files that are "not marked as generated code and are intended to be edited by the provider developer," including a `Read` method whose body is a `// Read API call logic` placeholder.

## What works

The IR is the reusable idea. It decouples the source of truth from the consumer, so OpenAPI, a hand-written spec, or a future generator can all feed the same Go generation step without the generator knowing where the spec came from. This is the same move [Magic Modules](magic-modules.md) makes with one YAML model, but here the format is published and versioned for outside consumers rather than internal to one toolchain.

The spec is typed for its consumers. Versioning follows JSON Schema MAJOR.MINOR for the schema and semantic versioning for releases, and the Go bindings give a consumer a compile-checked view of the IR instead of raw JSON.

The generated surface is the mechanical, high-volume part. For nested attributes the generator emits full custom type and value implementations (hundreds of lines of `ObjectTypable`/`ObjectValuable` boilerplate per attribute), which is exactly the code most error-prone to hand-write.

## What doesn't

The scope stops at structure. Per the docs, "the Framework Code Generator creates Plugin Framework schemas and helper functions for nested attributes." It does not generate Create, Update, Delete, drift handling, waiters, import, or tests, which is most of the hand-written volume in a real provider. The `scaffold` command's editable stubs are the admission: behavior is handed back to the developer as a placeholder comment.

Deriving from OpenAPI still requires hand-authored mapping. The generator config that names which operation is create versus read is written and maintained by a person, so "derive from the API spec" is really "derive the schema, author the operation map." [awscc](cloudformation-awscc.md) hit the related wall from the other side: an upstream spec that could not express the Terraform contract.

It has not graduated. Initial releases were `terraform-plugin-codegen-spec` v0.1.0 on 2023-10-16, and both `tfplugingen-openapi` and `tfplugingen-framework` v0.1.0 on 2023-10-17, each labeled "for Terraform Provider Code Generation tech preview." The latest releases are spec v0.2.0 (2024-09-09), openapi v0.3.0 (2024-01-19), and framework v0.4.1 (2024-09-24): all pre-1.0, none newer than September 2024, still tech preview and "NOT INTENDED FOR PRODUCTION USE" as read on 2026-10-16.

## Takeaways

An IR between source and consumer earns its keep only when sources or consumers are plural. This design justifies the serialized spec by letting many front ends share one back end. If you have one source and one target, you are paying for a decoupling you will not use.

Generation stops cleanly at schema and structure. Behavior resists it. A schema generator leaves CRUD, lifecycle, and tests untouched, so if your hand-written pain is behavior rather than attribute boilerplate, this shape does not reach it. The same boundary appears in [Upjet](upjet.md), which derives the schema and then asks for typed per-resource behavior.

"Derive first, author the residue" is real, but the residue here is both the operation mapping and all of CRUD, authored by hand. Budget for it as the main cost, not the leftover.

## Sources

- [Terraform plugin code generation overview](https://developer.hashicorp.com/terraform/plugin/code-generation) (read 2026-10-16)
- [Framework Code Generator](https://developer.hashicorp.com/terraform/plugin/code-generation/framework-generator) (read 2026-10-16)
- [OpenAPI Provider Spec Generator](https://developer.hashicorp.com/terraform/plugin/code-generation/openapi-generator) (read 2026-10-16)
- [terraform-plugin-codegen-spec README](https://github.com/hashicorp/terraform-plugin-codegen-spec/blob/main/README.md) (read 2026-10-16)
- [terraform-plugin-codegen-openapi README](https://github.com/hashicorp/terraform-plugin-codegen-openapi/blob/main/README.md) (read 2026-10-16)
- [terraform-plugin-codegen-spec releases](https://github.com/hashicorp/terraform-plugin-codegen-spec/releases) (read 2026-10-16)
- [terraform-plugin-codegen-openapi releases](https://github.com/hashicorp/terraform-plugin-codegen-openapi/releases) (read 2026-10-16)
- [terraform-plugin-codegen-framework releases](https://github.com/hashicorp/terraform-plugin-codegen-framework/releases) (read 2026-10-16)
