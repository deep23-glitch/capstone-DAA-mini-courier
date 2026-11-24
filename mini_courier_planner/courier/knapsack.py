"""Phase 2b: choose the best set of parcels for one trip (0/1 knapsack, DP).

dp[i][w] = best total value using only the first i parcels with capacity w.
    dp[i][w] = dp[i-1][w]                                   (skip parcel i)
             = max(dp[i-1][w], dp[i-1][w-wt] + val)         (take it, if wt <= w)
Time O(n*W), space O(n*W) (full table kept so we can backtrack and show it).
"""


def knapsack_dp(parcels, capacity):
    """Return (selected_parcels, total_value, dp_table)."""
    n = len(parcels)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        wt, val = parcels[i - 1].weight, parcels[i - 1].value
        row, prev = dp[i], dp[i - 1]
        for w in range(capacity + 1):
            row[w] = prev[w]
            if wt <= w and prev[w - wt] + val > row[w]:
                row[w] = prev[w - wt] + val
    # backtrack to recover which parcels were taken
    chosen, w = [], capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(parcels[i - 1])
            w -= parcels[i - 1].weight
    chosen.reverse()
    return chosen, dp[n][capacity], dp


def knapsack_greedy(parcels, capacity):
    """Value/weight greedy baseline (NOT optimal) - used to show why DP is needed."""
    chosen, load, total = [], 0, 0
    for p in sorted(parcels, key=lambda p: p.value / p.weight, reverse=True):
        if load + p.weight <= capacity:
            chosen.append(p); load += p.weight; total += p.value
    return chosen, total
