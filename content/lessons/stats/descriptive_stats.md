---
title: "Descriptive Statistics: Mean, Median, Mode, Variance"
order: 1
---

Descriptive statistics summarize a dataset's **center** and **spread** with a
handful of numbers, so you don't have to stare at every raw value.

## Center: mean, median, mode

- **Mean** -- the arithmetic average. Sensitive to outliers.
- **Median** -- the middle value when sorted. Robust to outliers.
- **Mode** -- the most frequent value. Useful for categorical data.

Example: incomes `[40k, 42k, 45k, 47k, 500k]`
- Mean = 134.8k (dragged way up by the 500k outlier)
- Median = 45k (much more representative of a "typical" income here)

## Spread: variance and standard deviation

- **Variance** -- the average squared distance from the mean.
- **Standard deviation** -- the square root of variance, back in the
  original units, so it's easier to interpret ("typical distance from
  the mean").

A small standard deviation means values cluster tightly around the mean;
a large one means they're spread out.

## When each measure misleads

The mean is misleading whenever outliers or skew are present -- home
prices, incomes, response times. The median survives that. Always plot
or at least skim your data before trusting a single summary number.

**Check yourself:** if a dataset's mean is much higher than its median,
what does that tell you about the shape of the distribution?
