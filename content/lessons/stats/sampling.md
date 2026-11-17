---
title: "Sampling"
order: 8
---

You almost never measure an entire population -- you measure a
**sample** and use it to infer things about the population. How you
pick that sample determines whether your conclusions are trustworthy.

## Population vs. sample

- **Population**: everyone/everything you actually care about (e.g.
  all users of an app).
- **Sample**: the subset you actually measure.

## Random sampling

Every member of the population has a known, non-zero chance of being
selected. This is what makes statistical inference (confidence
intervals, hypothesis tests) valid -- the math assumes the sample
represents the population fairly.

## Common sampling pitfalls

- **Selection bias**: your sampling method systematically favors
  certain kinds of members (e.g. surveying only people who answer
  their phone during business hours).
- **Sample size too small**: even a random sample can be noisy if it's
  tiny -- estimates swing wildly.
- **Non-response bias**: the people who *choose* to respond differ
  systematically from those who don't.

A large biased sample is often worse than a small random one --
size doesn't fix a broken sampling method.

**Check yourself:** if a survey is only sent by email, which parts of
the population might be systematically excluded?
