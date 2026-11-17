---
title: "Probability Distributions"
order: 3
---

A distribution describes how likely each possible value of a random
variable is. Instead of one number, you get a whole shape.

## Normal distribution

The classic bell curve: symmetric, most values cluster near the mean,
fewer values further away. Fully described by two parameters: mean
(center) and standard deviation (spread). Many natural measurements
(height, measurement error) roughly follow it, and the Central Limit
Theorem explains why it shows up so often even when the underlying data
isn't normal.

## Binomial distribution

Models the count of "successes" in a fixed number of independent
yes/no trials -- e.g. "how many heads in 10 coin flips?" Parameters: n
(number of trials) and p (probability of success on each trial). The
shape is discrete (bars, not a smooth curve) and becomes bell-shaped as
n grows.

## Reading a distribution

Before reaching for a formula, ask: is it symmetric or skewed? Discrete
(countable outcomes) or continuous (any value in a range)? Where's the
peak? That intuition tells you which formulas even apply.

**Check yourself:** would "number of customer support tickets per day"
be better modeled as normal or binomial-like (a count)?
