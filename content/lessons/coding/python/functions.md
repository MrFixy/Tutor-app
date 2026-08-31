---
title: "Functions"
order: 4
---

Think of a function as a reusable black box: inputs go in, an output
comes out, and the messy details stay hidden inside.

## Definition and call

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("Ada"))   # Hello, Ada!
```

## Parameters, arguments, return values

- **Parameters** are the names in the definition (`name` above).
- **Arguments** are the actual values you pass in (`"Ada"`).
- `return` sends a value back to the caller; without it, a function
  returns `None`.

## Default / optional arguments

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Ada"))               # Hello, Ada!
print(greet("Ada", "Hey"))        # Hey, Ada!
```
This is where beginners often trip: a default value is evaluated
**once**, when the function is defined -- so mutable defaults (like
`[]`) can behave surprisingly if you mutate them inside the function.

## Scope

Variables created inside a function only exist inside it -- they don't
leak out to the surrounding code.

**Check yourself:** what does `greet("Ada")` return if `greeting`'s
default is `"Hello"` and you don't pass a second argument?
