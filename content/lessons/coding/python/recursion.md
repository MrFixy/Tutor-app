---
title: "Recursion"
order: 5
---

Recursion is a function that calls itself, with a **base case** that
stops it from calling forever.

## Factorial example

```python
def factorial(n):
    if n == 0:              # base case: stops the recursion
        return 1
    return n * factorial(n - 1)
```

## Tracing the call stack

For `factorial(3)`:
```
factorial(3) = 3 * factorial(2)
factorial(2) = 2 * factorial(1)
factorial(1) = 1 * factorial(0)
factorial(0) = 1              <- base case hit, stack starts unwinding
```
So `factorial(3) = 3 * 2 * 1 * 1 = 6`. Each call waits for the one
below it to return before it can finish its own multiplication.

## The two required pieces

Every recursive function needs:
1. A **base case** that returns directly, without recursing.
2. A **recursive step** that moves *toward* that base case (here,
   `n - 1` gets closer to `0` every call).

Miss either one and you get infinite recursion, which Python stops
with a `RecursionError` once the call stack gets too deep.

**Check yourself:** what happens if you forget the base case entirely?
