# Tidying Software

What would Marie Kondo do with a codebase? I don't think she'd start by deleting things. Her method is mostly about deciding what to keep and where it lives. The deleting falls out of that.

She asks one question: does it spark joy? Software needs something else, because some of the most tedious code in a system is also essential. I use three questions, in this order:

1. **Does it earn its place?** There's always a historical reason something exists. Is there a present one?
2. **Does it belong here?** Is this where someone would look for it, and is it the only place the fact is written down?
3. **Does it make life easier for the next person?**

The order matters. There's no point finding the right home for something that shouldn't exist. And an elegant abstraction that makes everyone else's work harder doesn't pass just because it's elegant.

The first question does most of the work. When something is hard to organize, the trouble is usually that it shouldn't be there at all, and a better-designed home doesn't fix that. It just makes the clutter look tidy. A single control panel holding every setting for a resource is the classic case. It looks organized. It's a junk drawer with a nice front.

Tidying isn't the same as minimizing, though. Fewer lines don't mean less to understand. A 150-line implementation with boring control flow can be easier to live with than a 40-line generic one that needs a framework in your head to read. What matters is the burden on the reader, not the amount of material.

Perfection is the opposite trap. Three questions that can reject things will reject nearly anything, because little fully earns its place on a first pass. A change that leaves the system better than it found it has done its work, whether or not it arrives at the end state someone sketched. Holding out for the complete answer usually means keeping the current mess, and the mess was never the better option.

What keeps that from becoming an excuse is asking whether a step stands on its own. "This is progress toward something good" is how the AWS provider's testing vocabulary grew: every key was progress, and nobody was wrong about that. A step that only pays off if the rest of the plan lands is not a step, it is a down payment. A step that leaves things better even if everything after it is abandoned is worth taking now, at whatever size it comes in.

The part of her method I like most is thanking things before letting them go. Old code was usually right for its time. Annotations in the AWS provider came out of an effort to get away from a central registration file that caused merge conflicts, and most keys added since then solved a real problem for somebody. No single decision was the mistake. The accumulation was, and nobody chose that. It's easier to retire a design when you understand what it was for, and easier for the people who built it to agree to it.

So: keep what serves, give it one home, and let the rest go without contempt for whoever put it there.
