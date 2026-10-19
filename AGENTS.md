# AGENTS.md

Guidance for agents and people writing in this repository.

This repository collects how real systems model resources declaratively: where facts about a resource are written, what reads them, and what that costs. The aim is a reference someone can consult before designing their own, not a record of one project's decision.

It started as the research behind annotation changes in [terraform-provider-aws](https://github.com/hashicorp/terraform-provider-aws), and that work's findings and plan live here too.

## What belongs here

Anything added has to pass three tests, in order:

1. **Does it earn its place?** It tells the reader something they can't get faster elsewhere.
2. **Does it belong here?** It has one obvious home, and no other file already says it.
3. **Does it help the next reader?** It makes a design easier to understand, compare, or decide on.

Cutting is the default fix. Moving text to a better file is the second choice.

## Layout

```text
case-studies/                     one file per system or approach (magic-modules.md)
concepts/                         one idea per file that applies to any system (authority.md)
terraform-provider-aws/findings/  dated measurements of the provider, one topic per file
terraform-provider-aws/options/   the provider's design options, and the ones ruled out
terraform-provider-aws/plan/      what's decided for the provider and what happens next
```

Add a directory when there's content for it, not before. Use kebab-case filenames.

Every directory has a `README.md` that indexes its files: one line per file, giving the most important idea in it, not a description of what it covers. Update the index in the same change that adds, removes, or substantially changes a file.

Some content is general and some is about one project. A **concept** should make sense to someone who has never heard of the Terraform AWS provider. Anything specific to the provider, including its plan, goes under `terraform-provider-aws/`.

## Case studies

A case study covers one system. Use these sections, in this order, and leave out any that would be empty:

- **Summary**: one or two sentences. Who runs it and at what scale (Google's Terraform providers, thousands of Kubernetes controllers), then the single most useful thing to know about it. Readers decide whether to care based on who's doing it.
- **How it works**: where resource facts are authored (external file, IDL, comment markers, host-language values) and what consumes them (a generator, a shared runtime, both). A short real snippet if it helps.
- **What works**
- **What doesn't**
- **Takeaways**: what someone designing their own system should do or avoid because of this one. Not a summary of the sections above.
- **Sources**: links, each with the date it was read.

Link to other case studies instead of re-explaining them.

## Concepts

One idea per file. The first line states the idea as a claim. Then the mechanism, then at least one concrete example, preferably from a case study, linked. No Sources section is needed when every example links to a case study or finding.

## Findings

One topic per file. Each number says what was counted and when (a commit or a date), plus the command when it can be re-run. Measurements made before this repository existed may give the date and what was counted without the command. Findings report; they don't recommend. Recommendations go in `plan/`.

## Options

An option says what would change, a short sketch in real code, and what's good and bad about it. A rejected option keeps one line on why, so it isn't proposed again.

## Plan

The top says the status and its date. Decisions carry their reason in a sentence. Next steps are small pieces that are each worth doing even if the rest of the plan never happens. Parked items say what would bring them back.

## Evidence

This repository is public.

- Use public sources only. No internal figures, private conversations, or unreleased plans.
- Every factual claim traces to a source link, or to a measurement with its command, commit, and date.
- Prefer primary sources (code, official docs, issue threads) over write-ups about them.
- Quote exactly or not at all. Never invent an example, number, quotation, or anecdote.
- Numbers go stale. Give each one a date or a commit.
- One file owns each measurement. Anywhere else, cite the owner's number with a link to the owner, or leave it out. Never measure the same thing again in another file: two dated measurements of one thing are both right and read as a contradiction. When an owner's number changes, change its citations in the same commit.
- Mark judgment as judgment ("I think", "probably"). Don't present an opinion as a finding, or a finding as a hedge.
- Describe what a design was built to solve before saying where it falls short. Criticize designs, not the people who built them.

## Writing

Write for a technical reader who is busy and skeptical. They will skim first and read closely only if the first lines earn it.

- Put the point first. Supporting detail comes after, if at all.
- Be terse. Fragments are fine in lists and tables.
- State things; don't argue for them. No defending against objections the reader never raised, no justifying the document's structure.
- No meta narration: not "this document", "in this section", "as noted above", "it's worth noting", "let's look at".
- Write as the finished document. Nothing that refers to a prompt, a conversation, an earlier draft, or a reviewer.
- No em dashes. Use a comma, colon, period, or parentheses, or rewrite the sentence.
- Plain connectives: but, so, and, because, instead. Not however, moreover, furthermore, additionally, ultimately.
- Skip the usual filler: crucial, pivotal, robust, nuanced, leverage, landscape, delve, underscore, highlights, a testament to.
- Don't force symmetry. Not every list needs three items, and a weak side doesn't need a matching strong side. Give the important point the most words.
- No closing summary. End when the content ends.
- Use one name for one concept, and repeat it exactly. Don't swap in synonyms for variety.
- No private shorthand. Don't refer to things by labels a reader would have to look up (Q0, R2, J1, E2, §3.4). Name the thing, and link the file it lives in.
- Use a table when the reader is comparing things, a list when order matters or items are separate, and prose otherwise.
- Code snippets are real, short (about 15 lines or fewer), and show the point, not the setup.

## Size

Short files get read.

- Case study: 800 words or fewer.
- Any other file: 1,200 words or fewer.

Check with `wc -w <file>`. If a file is over, cut first. Split only when the parts make sense on their own.

## Before finishing

Run `python3 scripts/check.py`. It enforces the mechanical rules above: size, em dashes, filler words, meta narration, private shorthand, kebab-case names, local links, directory indexes, and case-study sections. CI runs the same script, and `--external` additionally checks every outbound link.

The script cannot check these, so check them yourself:

- Every claim has a source or a dated measurement.
- The first two lines would tell a skimmer whether to keep reading.
- The file earns its place, has one obvious home, and says nothing another file already says.
