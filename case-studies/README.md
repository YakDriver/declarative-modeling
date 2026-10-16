# Case studies

How real systems decide where facts about a resource are written and what reads them. Numbers are as of October 2026; each file has its sources.

| System | Who runs it | Facts authored in | Consumed by | The lesson |
|---|---|---|---|---|
| [Magic Modules](magic-modules.md) | Google's `google` and `google-beta` Terraform providers | external YAML | generator | Schema validation didn't stop one struct from reaching about 90 fields |
| [CloudFormation / awscc](cloudformation-awscc.md) | AWS CloudFormation; HashiCorp's `awscc` provider | external JSON Schema | generator | References are checked JSON pointers, but the spec can't express defaults, so awscc loses drift detection on omitted values |
| [tfplugingen](tfplugingen.md) | HashiCorp, tech preview since October 2023 | OpenAPI plus a JSON Schema IR | generator | Generates schema and models, not CRUD, waiters, import, or tests |
| [Pulumi](pulumi.md) | Every Pulumi provider, `pulumi-aws` bridged from the Terraform AWS provider | JSON schema, generated; typed Go mapping | generators and a shared runtime | A serialized spec pays off with six language targets |
| [Protobuf and Buf](protobuf-buf.md) | Google; Buf | IDL | generators and a separate toolchain | The format was cheap. Lint and breaking-change checks took a company and about eleven years |
| [Smithy](smithy.md) | AWS SDKs, including `aws-sdk-go-v2` | IDL | generator and a shared runtime | Models the API contract, not drift, diffs, or import |
| [controller-gen](controller-gen.md) | Kubernetes CRDs, at least 7,000 in open source | Go structs plus comment markers | generator | Misspelled markers are silently ignored |
| [controller-runtime](controller-runtime.md) | 26,454 importers on pkg.go.dev | Go code against one interface | shared runtime | One small typed interface scales with no metadata language |
| [Upjet](upjet.md) | Crossplane's official AWS, Azure, and GCP providers; 1,062 AWS resources | derived from Terraform schemas, residue in typed Go | generator and a shared runtime | Derive first, author what's left. References to schema fields stay strings |
| [ent](ent.md) | Started at Meta; Linux Foundation project | typed Go | generator | Typed Go doesn't imply a shared runtime |
| [Go struct tags](go-struct-tags.md) | Go standard library | string tags | runtime reflection | Strings are fine while the vocabulary stays tiny |
| [database/sql](database-sql.md) | Over 200,000 importers | a name plus a typed interface | shared runtime | Capabilities as optional interfaces, not flags |
| [Terraform AWS provider annotations](terraform-provider-aws-annotations.md) | About 2,700 registrations in the AWS provider | comment markers | generators | The same silent failures as controller-gen, at smaller scale |

## The two choices

Where facts are authored and what consumes them are separate decisions. Every combination is in use:

| | Generator | Shared runtime |
|---|---|---|
| External file or IDL | Magic Modules, awscc, tfplugingen, Protobuf | Smithy (with a generator), Pulumi (with a generator) |
| Comment markers | controller-gen, Terraform AWS provider | |
| Host-language values | ent, Upjet | controller-runtime, Upjet, `database/sql` |

None of these systems pairs comment markers with a shared runtime. Comments don't survive compilation, so only a generator can read them.

## Patterns that show up more than once

- **Checked references.** CloudFormation's JSON pointers, Pulumi's `$ref` tokens, and ent's `Car.Type` all fail when the target doesn't exist. Comment markers and struct tags don't.
- **Derive first.** Upjet and the Pulumi bridge take everything they can from the Terraform schema and ask only for the remainder.
- **Defaults omitted on write.** Magic Modules strips default values when writing YAML, so authored files shrink as defaults are added.
- **Unknown keys fail open.** controller-gen and the Terraform AWS provider both ignore keys they don't recognize. Neither format checks itself. The checker is separate work.
- **Escape hatches.** Magic Modules has `custom_code` and handwritten resources. awscc suppresses resources with the reason in a comment. Every generate-everything system needs one.
