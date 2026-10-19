# Terraform AWS provider

Research behind changing how [terraform-provider-aws](https://github.com/hashicorp/terraform-provider-aws) annotates its resources. The team-agreed [principles](https://github.com/hashicorp/terraform-provider-aws/blob/main/docs/design-decisions/declarative-resource-modeling-principles.md) live in the provider.

- [The problem](problem.md): one comment language does four jobs and accepts wrong keys silently, and writing annotations is no longer the expensive part.
- [Findings](findings/README.md): dated measurements of the annotation surface, its generators, and what the provider reads.
- [Options](options/README.md): every design option considered, the criteria for judging them, and what's ruled out.
- [Plan](plan/README.md): what's decided and the next small pieces.
