---
title: "Hypothesis Testing"
order: 4
---

Hypothesis testing is a courtroom for data: you assume innocence (the
"null hypothesis") until the evidence is strong enough to reject it.

## The two hypotheses

- **Null hypothesis (H0)**: "nothing interesting is happening" --
  e.g. "this new button color has no effect on click rate."
- **Alternative hypothesis (H1)**: what you suspect instead -- e.g.
  "the new button color changes click rate."

You never "prove" H0 true; you either reject it or fail to reject it,
same as a jury returning "not guilty" rather than "innocent."

## Test statistic and decision rule

1. Collect data and compute a **test statistic** that measures how far
   your data is from what H0 predicts.
2. Compare it to a threshold (often via a p-value, see the next
   lesson).
3. If the evidence against H0 is strong enough, reject it in favor of
   H1.

## Two ways to be wrong

- **Type I error**: rejecting H0 when it's actually true (false
  alarm).
- **Type II error**: failing to reject H0 when it's actually false
  (missed effect).

There's a trade-off between the two -- tightening the threshold to
avoid one type of error loosens it for the other.

**Check yourself:** in a courtroom analogy, which error is "convicting
an innocent person"?
