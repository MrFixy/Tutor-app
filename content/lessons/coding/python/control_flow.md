---
title: "Control Flow: Conditionals and Loops"
order: 3
---

Control flow determines which lines of code actually run, and how
many times.

## if / elif / else

```python
score = 72
if score >= 90:
    grade = "A"
elif score >= 70:
    grade = "B"
else:
    grade = "C"
```
Python checks conditions top to bottom and runs the **first** branch
that matches, then skips the rest.

## for loops

```python
for n in [10, 20, 30]:
    print(n * 2)   # 20, 40, 60 -- iterates over each item directly
```

## while loops

```python
count = 0
while count < 3:
    print(count)
    count += 1     # must change or the loop never ends
```

## Tracing execution

For `score = 72` above: Python checks `score >= 90` -> False, moves to
`elif score >= 70` -> True, sets `grade = "B"`, then **skips** the
`else` entirely since a branch already matched.

**Check yourself:** what would `grade` be if `score = 65`?
