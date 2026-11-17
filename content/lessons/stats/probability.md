---
title: "Probability Basics"
order: 2
---

Probability measures how likely an event is, as a number between 0
(impossible) and 1 (certain).

## Building blocks

- **Experiment**: rolling a die, flipping a coin, drawing a card.
- **Outcome**: one possible result (e.g. "rolled a 4").
- **Event**: a set of outcomes you care about (e.g. "rolled an even
  number").

P(event) = (favorable outcomes) / (total possible outcomes), when
outcomes are equally likely.

Example: P(rolling an even number on a fair 6-sided die) = 3/6 = 0.5.

## Independent vs. dependent events

- **Independent**: one event doesn't affect the other's probability.
  Flipping a coin twice -- the second flip doesn't care about the first.
  P(A and B) = P(A) x P(B).
- **Dependent**: one event changes the probability of the other.
  Drawing two cards *without replacement* -- the deck composition
  changes after the first draw.

## Complement rule

P(not A) = 1 - P(A). Often easier to compute the complement and
subtract than the event directly (e.g. "at least one heads in 3 flips"
is easier via 1 - P(no heads at all)).

**Check yourself:** if you draw one card from a standard deck, what's
P(drawing a heart)?
