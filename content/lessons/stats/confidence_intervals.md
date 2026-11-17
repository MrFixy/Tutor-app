---
title: "Confidence Intervals"
order: 6
---

A confidence interval gives you a *range* of plausible values for an
unknown quantity, instead of a single point estimate that's almost
certainly not exactly right.

## The idea

Instead of saying "the average commute time is 32 minutes," you say
"we're 95% confident the true average is between 29 and 35 minutes."
That range communicates your uncertainty honestly.

## What "95% confidence" means

It does **not** mean "there's a 95% chance the true value is in this
particular interval." It means: if you repeated the sampling process
many times and built an interval each time, about 95% of those
intervals would contain the true value. The confidence is in the
*method*, not any single interval.

## Width depends on

- **Sample size**: bigger samples -> narrower intervals (more
  precision).
- **Variability in the data**: more spread -> wider intervals.
- **Confidence level**: wanting more confidence (99% vs 95%) -> wider
  intervals, since you're casting a wider net to be more sure.

**Check yourself:** would a 99% confidence interval be wider or
narrower than a 95% one, for the same data?
