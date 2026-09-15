---
title: "Python Syntax Basics"
order: 1
---

Every Python program is built from a small set of basics: variables,
types, printing, and operators.

## Variables and types

```python
name = "Ada"       # str
age = 28           # int
height = 1.7        # float
is_admin = False    # bool
```

Python is dynamically typed -- you don't declare a type, and a
variable can be reassigned to a different type later (though doing so
on purpose is usually a code smell).

## Printing

```python
print("Hello,", name)          # Hello, Ada
print(f"{name} is {age}")      # f-strings: the standard way to embed values
```

## Operators

- Arithmetic: `+ - * / // % **` (`//` is floor division, `**` is power)
- Comparison: `== != < > <= >=`
- Logical: `and or not`

## Common beginner pitfalls

- `=` assigns, `==` compares -- mixing them up is the single most
  common beginner typo.
- Indentation is syntax in Python, not style -- mismatched indentation
  is a real error (`IndentationError`), not just ugly.
- `/` always returns a float in Python 3, even `4 / 2` gives `2.0`.

**Check yourself:** what does `7 // 2` evaluate to, and how is it
different from `7 / 2`?
