---
title: "Debugging"
order: 7
---

Debugging is a systematic process, not guesswork -- learning to read
an error message and narrow down where things went wrong is the actual
skill.

## Reading a traceback

Python's error output (a traceback) tells you, from top to bottom, the
chain of calls that led to the error, ending with the actual exception
type and message at the bottom:

```
Traceback (most recent call last):
  File "main.py", line 7, in <module>
    total = add(prices)
  File "main.py", line 3, in add
    return sum(prices) / len(prices)
ZeroDivisionError: division by zero
```
Read the **last line first** (what went wrong), then the line right
above it (where, in your own code) -- that's usually the fastest way
in.

## A systematic process

1. **Reproduce** the bug reliably -- an intermittent bug is much
   harder to fix than one you can trigger every time.
2. **Isolate**: narrow down which line/function is responsible, e.g.
   with `print()` statements or a debugger, by checking values at each
   step.
3. **Form a hypothesis** about the cause before changing code --
   changing things at random tends to create new bugs.
4. **Fix and verify**: make the smallest change that addresses the
   hypothesis, then re-run to confirm.

## Don't just copy the fix

If you ask for help debugging, understanding *why* the bug happened
prevents the same mistake next time -- the diagnostic process matters
more than the specific line changed.

**Check yourself:** in the traceback above, what caused the
`ZeroDivisionError`?
