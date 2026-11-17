---
title: "Python Data Structures"
order: 2
---

Python's built-in data structures each solve a different access
pattern -- picking the right one is about matching the structure to
how you'll use the data, not memorizing syntax.

## List -- ordered, indexed

```python
scores = [90, 85, 77]
scores.append(100)
print(scores[0])       # 90 -- lookup by position
```
Fast at: appending, iterating in order. Slower at: searching for a
value.

## Dict -- key-value lookup

```python
scores = {"alice": 90, "bob": 85}
scores["cara"] = 77     # add a new key
print(scores["bob"])    # 85 -- lookup by meaningful key, O(1)
```
Use when you think "I need to look this up by name/id."

## Set -- unique, unordered

```python
seen = {1, 2, 3}
seen.add(2)              # no-op, 2 is already in the set
print(3 in seen)         # True -- fast membership test
```
Use for deduplication and fast "is this in the collection?" checks.

## Tuple -- ordered, immutable

```python
point = (3, 4)
```
Like a list but can't be changed after creation -- useful for fixed
groupings (coordinates, RGB values) and as dict keys (lists can't be).

**Check yourself:** which structure would you use to store a student's
test scores in the order they were taken?
