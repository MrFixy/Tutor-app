---
title: "P-Values and Statistical Significance"
order: 5
---

A p-value is one of the most misunderstood numbers in statistics --
let's get the definition exactly right before anything else.

## What a p-value actually is

**A p-value is the probability of seeing data at least as extreme as
what you observed, *assuming the null hypothesis is true*.**

It is **NOT**:
- the probability that the null hypothesis is true
- the probability that your result is "due to chance" in some vague
  sense
- the probability that you'd get the same result if you repeated the
  experiment

A small p-value means: "if there really were no effect, data like this
would be rare" -- which is evidence against the null hypothesis, not a
verdict on it.

## Significance level (alpha)

Before the test, you pick a threshold -- commonly 0.05 -- called alpha.
If p < alpha, the result is "statistically significant": the evidence
against H0 clears your pre-chosen bar.

## Significance isn't the same as importance

A tiny, practically meaningless effect can still be "statistically
significant" with a large enough sample size. Always look at the
effect size alongside the p-value, not the p-value alone.

**Check yourself:** if p = 0.03 and alpha = 0.05, do you reject or fail
to reject the null hypothesis?
