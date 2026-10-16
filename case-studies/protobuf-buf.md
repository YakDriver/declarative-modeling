# Protocol Buffers and Buf

## Summary

Protocol Buffers is Google's IDL for serializing structured data, open-sourced in July 2008 and, per protobuf.dev, "the most commonly-used data format at Google." For over a decade the format shipped with a code generator and little else. Buf, a venture-backed company, later built the linting, formatting, breaking-change detection, and registry around it. The lesson worth taking: the IDL was the cheap part, the toolchain was the expensive part.

## How it works

Resource facts live in `.proto` files, an external IDL. protobuf.dev describes Protobuf as "a combination of the definition language (created in `.proto` files)", the compiler-generated code, language runtime libraries, and the wire format. A field is a name, a type, and a tag number:

```proto
edition = "2023";

message Person {
  string name = 1;
  int32 id = 2;
  string email = 3;
}
```

Two kinds of consumer read the same files. `protoc` and its plugins generate code in many languages. Buf's toolchain reads them for lint, format, and compatibility checks, and the Buf Schema Registry (BSR) hosts and versions them.

## What works

`buf breaking` "compares the current version of your Protobuf schema against a past version and reports any changes that would break clients, servers, or the code generated from those schemas." It groups rules into four categories from strict to lenient: `FILE`, `PACKAGE`, `WIRE_JSON`, `WIRE`. Passing a stricter category implies passing every looser one, so one spec serves consumers with different coupling: a wire-only consumer tolerates `WIRE`, a consumer of generated Go needs `PACKAGE`. Compatibility becomes machine-checkable against a prior version.

Enforcement runs in three places: locally, in CI, and server-side on the BSR, where a push that would break consumers enters a review flow before it reaches production. Server-side checks do not depend on local configuration, so a rule cannot be skipped by editing a local file.

Lint has its own categorized rules (`MINIMAL`, `BASIC`, `STANDARD`, `COMMENTS`, `UNARY_RPC`). Formatting is one command. The toolchain, not the format, delivers all of this.

## What doesn't

The format alone delivered none of it. `protoc` has existed since the 2008 open-source release and gives code generation only. Lint, format, breaking detection, and a registry arrived with Buf: first public commit October 2019 (message "Copy from internal"), CLI v1.0.0 in February 2022, built by a company that raised a $3.7M seed round in September 2020. Roughly eleven years separated the open-source format from a mature toolchain on top of it.

Expressiveness is bounded. Protobuf models message shape (fields, types, tag numbers), not behavior or lifecycle. [Smithy](smithy.md), in the same IDL family, hits the same wall.

## Takeaways

- Choosing an IDL buys a format, and you still owe the toolchain. Budget for the validator, the compatibility checker, and the registry as separate work. On Protobuf that work took a funded company years, on a format that already existed.
- A machine-checkable compatibility gate is the strongest reason to put metadata in an external spec. A tool that diffs the spec across versions catches breakage a human review misses.
- Put enforcement where it cannot be skipped. Buf's server-side BSR checks run regardless of local config. Rules that live only in a local linter get bypassed.
- Layered strictness (`FILE` > `PACKAGE` > `WIRE_JSON` > `WIRE`) lets one spec serve consumers that depend on different layers. Design the levels before writing the rules.
- The spec's value scales with tooling, not syntax. Adopt an external IDL but never build the checks and you have paid for the costliest thing (another file to keep correct) with none of the return.

## Sources

- Overview, protobuf.dev. read 2026-10-16.
- "Protocol Buffers: Google's Data Interchange Format," Google Open Source Blog, July 2008 (https://opensource.googleblog.com/2008/07/protocol-buffers-googles-data.html). read 2026-10-16.
- Detecting breaking changes, buf.build/docs (https://buf.build/docs/breaking/). read 2026-10-16.
- Linting rules and categories, buf.build/docs (https://buf.build/docs/lint/rules/). read 2026-10-16.
- bufbuild/buf v1.0.0 release, published 2022-02-17 (https://github.com/bufbuild/buf/releases/tag/v1.0.0). read 2026-10-16.
- bufbuild/buf first public commit, 2019-10-18 (https://github.com/bufbuild/buf/commit/157c7ae554844ff7ae178536ec10787b5b74b5db). read 2026-10-16.
- "An update on our fundraising," Buf Blog (September 2020 seed, Lightspeed) (https://buf.build/blog/an-update-on-our-fundraising). read 2026-10-16.
