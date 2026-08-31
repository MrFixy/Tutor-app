---
title: "Algorithms: Sorting, Searching, and Big-O"
order: 6
---

An algorithm is just a step-by-step recipe for solving a problem. This
lesson covers the intuition behind the most common ones, plus how to
talk about their speed.

## Searching: binary search

Binary search is like guessing a number by repeatedly halving the
range: "is it higher or lower than the middle?" On a **sorted** list of
size n, it finds a value in about log2(n) steps instead of checking
every element one by one.

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

## Sorting

Common algorithms (merge sort, quicksort) rearrange a list into order.
You rarely write these by hand in practice (`sorted()` / `.sort()` do
it) but understanding the *idea* -- repeatedly compare-and-swap or
divide-and-conquer -- helps you reason about performance.

## Big-O, in plain terms

Big-O describes how an algorithm's running time grows as the input
grows, ignoring constant factors:
- **O(1)**: constant -- same speed regardless of input size (dict
  lookup).
- **O(log n)**: grows very slowly -- binary search.
- **O(n)**: grows linearly -- checking every element once.
- **O(n^2)**: grows quadratically -- comparing every pair.

**Check yourself:** why does binary search require the list to be
sorted first?
