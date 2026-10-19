# Software KonMari: what a system keeps, and why

Deciding what a codebase keeps, where each thing lives, and how to retire a design that stopped earning its place.

What would Marie Kondo do with a codebase? I don't think she'd start by deleting things. Her method is mostly about deciding what to keep and where it lives. The deleting falls out of that.

She asks one question: does it spark joy? Software needs something else, because some of the most tedious code in a system is also essential. I use three questions, in this order:

1. **Does it earn its place?** There's always a historical reason something exists. Is there a present one?
2. **Does it belong here?** Is this where someone would look for it, and is it the only place the fact is written down?
3. **Does it make life easier for the next person?**

The order matters. There's no point finding the right home for something that shouldn't exist. And an elegant abstraction that makes everyone else's work harder doesn't pass just because it's elegant.

The first question does most of the work. When something is hard to organize, the trouble is usually that it shouldn't be there at all, and a better-designed home doesn't fix that. It just makes the clutter look organized. A single control panel holding every setting for a resource is the classic case. It's a junk drawer with a nice front.

Keeping less isn't the same as minimizing lines, though. Fewer lines don't mean less to understand. A 150-line implementation with boring control flow can be easier to live with than a 40-line generic one that needs a framework in your head to read. What matters is the burden on the reader, not the amount of material.

Perfection is the opposite trap. Three questions that can reject things will reject nearly anything on a first pass, and holding out for the complete answer usually means keeping the current mess. What keeps "it's a step" from becoming an excuse is asking whether the step [stands on its own](concepts/steps-stand-alone.md): if everything planned after it were abandoned, would the system still be better? Every key in the AWS provider's testing vocabulary was progress toward something, and that's how the vocabulary grew.

The part of her method I like most is thanking things before letting them go. Old code was usually right for its time. Annotations in the AWS provider came out of an effort to get away from a central registration file that caused merge conflicts, and most keys added since then solved a real problem for somebody. No single decision was the mistake. The accumulation was, and nobody chose that. It's easier to retire a design when you understand what it was for, and easier for the people who built it to agree to it.

So: keep what serves, give it one home, take the step that stands on its own, and let the rest go without contempt for whoever put it there.
