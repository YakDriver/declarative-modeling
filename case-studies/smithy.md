# Smithy

## Summary

Smithy is AWS's interface definition language for services, "based on an interface definition language that has been widely used within Amazon and AWS for over a decade." One model generates SDKs across many languages, including Go via smithy-go, which "powers aws-sdk-go-v2." The useful lesson here is about warrant: Smithy exists because AWS publishes one API to many language targets, and that condition, not the format itself, is what justifies a purpose-built IDL. A Terraform provider has one target and a different job.

## How it works

Facts about an API are authored in a purpose-built IDL. The building blocks are shapes (simple, aggregate, and service types), operations, and traits. Traits are the extension mechanism: "Traits are used to extend a model and add capabilities that are not part of the core specification." The spec is "an interface definition language and set of tools used to build clients, servers, and other kinds of artifacts through model transformations," with a built-in validation system over a normalized semantic model.

What consumes the model is both a generator and a shared runtime. smithy-go is "a Java/Gradle-based Smithy build plugin that generates Go client, server, and shape code from Smithy models," plus a runtime module (`github.com/aws/smithy-go`: middleware, transport, auth, endpoints) that "the generated code depends on." Protocol is decoupled from shapes, so one model serializes over restJson1, awsJson, restXml, query, or rpcv2Cbor.

Smithy reaches further into behavior than most IDLs. Waiters are modeled as a trait: polling an API until a server-reported state is reached.

```smithy
@waitable(
    BucketExists: {
        acceptors: [
            { state: "success", matcher: { success: true } }
            { state: "retry", matcher: { errorType: "NotFound" } }
        ]
    }
)
operation HeadBucket { input: HeadBucketInput, output: HeadBucketOutput, errors: [NotFound] }
```

## What works

A genuine multi-language warrant. AWS must ship SDKs in Java, TypeScript, Rust, Python, Kotlin, Go, and more, and "Smithy models were designed for the purpose of generating code for multiple programming languages." When the consumers are that heterogeneous, a serialized language-independent spec earns its keep. This is the same condition that justifies [Pulumi](pulumi.md)'s schema and distinguishes it from a single-target provider.

Extensible, validated vocabulary. Traits add capability without changing the core, and models are validated against configurable rules before anything is generated. New AWS concepts arrive as decoupled trait packages rather than format revisions.

Generator and shared runtime coexist. Serialization, retries, endpoint resolution, and auth live in the runtime module, not in per-operation generated code, so the generated surface stays thin. The split mirrors [controller-runtime](controller-runtime.md): generate the shape, share the behavior.

## What doesn't

Smithy models the API contract, the request and response shapes an operation exchanges. It does not model how a stateful consumer reconciles that API against desired configuration. The hard parts of a Terraform provider live in that gap:

- Drift detection: comparing prior state to live reality, independent of any single call.
- Diff suppression: deciding when a server-normalized value equals the configured one.
- Import: adopting an existing resource with no prior state.
- Plan modification and replacement semantics: `ForceNew`, defaults, computed values.

Smithy waiters are the sharp edge of this boundary. They poll an API toward a server-defined state ("a client-side abstraction used to poll a resource until a desired state is reached"). A provider's wait logic is often tied instead to Terraform's state machine and eventual consistency between calls, which the model never sees.

## Takeaways

- Count the consumers before choosing an IDL. One serialized model pays off when the targets are many and language-independent. With a single host language, typed values in that language (see [ent](ent.md), [Upjet](upjet.md)) give checked references for free that an IDL string cannot.
- An IDL can reach into behavior, but only behavior that is a property of the API. Smithy models waiters and pagination because the server defines them. Drift, diff, and import are properties of the reconciler, not the API, so no API IDL will supply them. Compare [awscc](cloudformation-awscc.md), where an upstream AWS spec also could not express the Terraform contract.
- Separate the generator from the runtime deliberately. smithy-go keeps serialization and retries in a shared module so generated code stays thin. Decide which facts are shape (generate) and which are behavior (share) before writing either.

## Sources

- Smithy specification, interface definition language framing (read 2026-10-16): https://smithy.io/2.0/spec/index.html
- The Smithy model, shapes and traits, semantic model (read 2026-10-16): https://smithy.io/2.0/spec/model.html
- Smithy home and FAQ, decade of internal use, multi-language codegen, traits (read 2026-10-16): https://smithy.io/2.0/index.html
- Smithy Waiters additional spec, `@waitable` and the S3 `BucketExists` example (read 2026-10-16): https://smithy.io/2.0/additional-specs/waiters.html
- smithy-go README, generator plus runtime, "powers aws-sdk-go-v2" (read 2026-10-16): https://github.com/aws/smithy-go/blob/main/README.md
- aws-sdk-go-v2 README, codegen build, service clients (read 2026-10-16): https://github.com/aws/aws-sdk-go-v2/blob/main/README.md
