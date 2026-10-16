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
case-studies/   one file per system or approach, kebab-case (magic-modules.md)
```

Add a directory when there's content for it, not before.

## Case studies

A case study covers one system. Use these sections, in this order, and leave out any that would be empty:

- **Summary**: one or two sentences. What it is and the single most useful thing to know about it.
- **How it works**: where resource facts are authored (external file, IDL, comment markers, host-language values) and what consumes them (a generator, a shared runtime, both). A short real snippet if it helps.
- **What works**
- **What doesn't**
- **Takeaways**: what someone designing their own system should do or avoid because of this one. Not a summary of the sections above.
- **Sources**: links, each with the date it was read.

Link to other case studies instead of re-explaining them.

## Evidence

This repository is public.

- Use public sources only. No internal figures, private conversations, or unreleased plans.
- Every factual claim traces to a source link, or to a measurement with its command, commit, and date.
- Prefer primary sources (code, official docs, issue threads) over write-ups about them.
- Quote exactly or not at all. Never invent an example, number, quotation, or anecdote.
- Numbers go stale. Give each one a date or a commit.
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
- Use a table when the reader is comparing things, a list when order matters or items are separate, and prose otherwise.
- Code snippets are real, short (about 15 lines or fewer), and show the point, not the setup.

## Size

Short files get read.

- Case study: 800 words or fewer.
- Any other file: 1,200 words or fewer.

Check with `wc -w <file>`. If a file is over, cut first. Split only when the parts make sense on their own.

## Before finishing

- `wc -w` is under the limit.
- No em dashes: `grep -n '—' <file>` returns nothing.
- Every claim has a source or a dated measurement.
- The first two lines would tell a skimmer whether to keep reading.
