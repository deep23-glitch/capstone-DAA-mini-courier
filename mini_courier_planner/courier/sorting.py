"""Phase 2a: parcel prioritisation.

Sort key: earliest deadline first, ties broken by higher priority.
Merge sort is used as the main algorithm: O(n log n) in every case and stable.
Insertion sort and Python's Timsort are included only for the Phase 4 comparison.
"""


def _key(p):
    return (p.deadline, -p.priority, p.pid)


def merge_sort(items, key=_key):
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out


def insertion_sort(items, key=_key):
    a = list(items)
    for i in range(1, len(a)):
        cur, j = a[i], i - 1
        while j >= 0 and key(a[j]) > key(cur):
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = cur
    return a


def builtin_sort(items, key=_key):
    return sorted(items, key=key)
