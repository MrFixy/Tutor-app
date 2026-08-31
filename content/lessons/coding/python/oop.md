---
title: "Object-Oriented Programming"
order: 8
---

Object-oriented programming organizes code around **objects** --
bundles of data and the behavior that acts on it.

## Class = blueprint, object = the thing built from it

```python
class Dog:
    def __init__(self, name):
        self.name = name          # instance data

    def bark(self):
        return f"{self.name} says woof!"

rex = Dog("Rex")        # rex is an *instance* (object) of class Dog
print(rex.bark())       # Rex says woof!
```
Think of `Dog` as a house blueprint and `rex` as one actual house built
from it -- you can build many houses (objects) from the same blueprint
(class), each with its own data.

## Methods vs. attributes

- **Attributes** are the data stored on an object (`self.name`).
- **Methods** are functions defined inside the class that act on that
  data (`bark`).

## Inheritance

```python
class Puppy(Dog):
    def bark(self):
        return f"{self.name} says yip!"   # overrides Dog's bark
```
`Puppy` inherits everything from `Dog` but can override specific
methods -- useful when a new class is "a kind of" an existing one with
some differences.

**Check yourself:** if you create two `Dog` objects with different
names, do they share the same `name` attribute or each have their own?
