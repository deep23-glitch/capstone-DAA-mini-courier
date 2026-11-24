---
title: "Mini-Courier Planner – Capstone Report"
subtitle: "Design & Analysis of Algorithms (ETCCDA302) · K.R. Mangalam University"
---

**Student:** Deep Saha  **Roll no.:** 2501010058  **Faculty:** Dr. Shweta Agarwal

# 1. Phase 1 – Problem design and planning

**Problem.** A courier van starts at a depot with a set of pending parcels. It can carry at most *W* kg per trip. The planner must decide which parcels to load, in what order to deliver them, and over which roads, so that urgent and high-priority parcels go first and the distance driven is small.

**Data design.**

| Entity | Fields |
|---|---|
| Parcel | id, weight (integer kg), priority (1–5), deadline (hours), destination node |
| Road graph | undirected, weighted (km); adjacency list; edges stored as `[u, v, km]` |
| Vehicle | capacity W (kg), average speed (30 km/h), start/end at depot (node 0) |

A parcel's *value* is `priority × 10 + max(0, 12 − deadline)`, so priority and urgency both raise the chance of being loaded.

**Algorithm selection and how they fit together.**

| Step | Technique | Why this one |
|---|---|---|
| 1. Prioritise | Merge sort (deadline ↑, priority ↓) | Guaranteed O(n log n), stable, and easy to trace |
| 2. Pack | 0/1 knapsack, dynamic programming | Each parcel is taken whole or not at all; greedy by ratio is not always optimal |
| 3. Distances | Dijkstra (binary heap) | Non-negative road lengths; gives real road distances between stops |
| 4. Route | Nearest-neighbour TSP (+ optional 2-opt) | Exact TSP is NP-hard; a greedy approximation is fast and measurable |

**Data flow.** parcels → *sort* → *knapsack* → chosen parcels → their destinations are the stops → *Dijkstra* from every stop gives a k×k distance matrix → *nearest neighbour* orders the stops → shortest road paths are stitched into the full route → ETA per stop is compared with deadlines.

# 2. Phase 2 – Package prioritisation and box filling

**Sorting.** `courier/sorting.py::merge_sort` orders parcels by (deadline, −priority, id). Output on the small dataset (first rows):

| ID | Wt | Priority | Deadline | Dest | Value |
|---|---|---|---|---|---|
| 10 | 17 | 4 | 3 | 11 | 49 |
| 8 | 21 | 1 | 5 | 9 | 17 |
| 6 | 4 | 5 | 11 | 9 | 51 |

**Dynamic programming.** `dp[i][w]` is the best value using the first *i* parcels with capacity *w*:
`dp[i][w] = max(dp[i−1][w], dp[i−1][w−wᵢ] + vᵢ)`. Backtracking through the table recovers the chosen parcels. On the small dataset (W = 60 kg) the plan loads parcels **3, 4, 6, 10** – exactly 60 kg, total value 180. The unit tests compare the DP with exhaustive search on 30 random instances and it always matches.

**Why DP rather than greedy.** A value-per-kg greedy baseline is included. Over 200 random instances (15 parcels, W = 60) greedy returned a worse load in 85 (42.5 %), losing 1.6 % of value on average. DP is never worse.

![Console output – small dataset](../outputs/screenshot_run_small.png)

# 3. Phase 3 – Route maker and graph processing

**Graph.** An adjacency list built from the edge list; every node is connected to its three nearest neighbours plus a spanning tree, so the graph is always connected.

**Dijkstra.** Run from the depot and from every delivery stop, using `heapq`; stale heap entries are skipped. The predecessor array is used to rebuild actual road paths. The implementation was checked against Floyd–Warshall on a 25-node graph and on a hand-solved example, including an unreachable node.

**Nearest-neighbour TSP.** From the depot, repeatedly go to the closest unvisited stop (by Dijkstra distance), then return to the depot. Small dataset result:

`Depot → Golf Course Rd (9.5) → Huda City Centre (22.5) → Badshahpur (10.9) → DLF Phase 3 (30.9) → Depot (32.3)` = **106.1 km**.

Full road path (node ids): 0 > 5 > 0 > 2 > 9 > 11 > 9 > 8 > 2 > 0. Roads are re-used because shortest paths between stops pass through intermediate nodes (here the depot itself).

**Quality of the approximation.** On 30 random 8-stop instances in a 300-node graph, compared with the brute-force optimum: nearest neighbour averaged **1.078×** optimal (worst 1.294×); with 2-opt, **1.003×** average (worst 1.056×).

# 4. Phase 4 – Performance testing and optimisation

**Test cases (12 unit tests, all passing).** Sorting vs built-in sort, empty/single input, tie-breaking; knapsack vs brute force, DP ≥ greedy, zero capacity; Dijkstra vs Floyd–Warshall and unreachable nodes; tour validity and ordering opt ≤ 2-opt ≤ NN; capacity respected; every parcel assigned exactly once across trips.

**Datasets.** small (12 nodes, 10 parcels), medium (60, 40), large (300, 200), plus scaled synthetic inputs in `benchmark.py`. Times are best-of-3 wall-clock on a cloud container; absolute values vary by machine, the growth trends are what matter.

![Sorting runtime](../outputs/chart_sorting.png){width=60%}

**Sorting.** At n = 3200: merge sort 12.8 ms, insertion sort 362 ms, built-in Timsort 0.86 ms. Insertion sort grows roughly 4× per doubling of n between 100 and 1600 (O(n²)), while merge sort grows a little over 2× (O(n log n)). Timsort wins because it is implemented in C.

![Knapsack runtime](../outputs/chart_knapsack.png)

**Knapsack.** Time is linear in both n and W (n = 800, W = 200: 13 ms; n = 200, W = 1600: 52 ms), as O(n·W) predicts. W is a pseudo-polynomial factor: the DP is cheap for a van in kilograms but would be costly if weights were in grams.

![Dijkstra runtime](../outputs/chart_dijkstra.png){width=60%}

**Dijkstra.** Near-linear growth with sparse graphs (V = 1600, E ≈ 3300: 0.89 ms per source). Running it from every stop is what dominates the end-to-end time on the large dataset.

![TSP](../outputs/chart_tsp.png)

**TSP.** Nearest neighbour at k = 160 stops takes 2.9 ms; 2-opt cuts the route from 554 km to 455 km (−18 %) but costs 25 ms.

![Pipeline](../outputs/chart_pipeline.png){width=70%}

| Dataset | Sort (ms) | Knapsack (ms) | Dijkstra (ms) | TSP-NN (ms) |
|---|---|---|---|---|
| small (12 / 10) | 0.02 | 0.05 | 0.04 | 0.01 |
| medium (60 / 40) | 0.06 | 0.33 | 0.48 | 0.03 |
| large (300 / 200) | 0.31 | 3.81 | 8.33 | 0.16 |

**Findings and optimisation suggestions.**

1. On larger inputs the Dijkstra runs and the knapsack table dominate; sorting and NN are negligible. Dijkstra could stop early once all stops are settled, or reuse results between trips.
2. The knapsack keeps the full n×W table only to backtrack; a 1-D table plus a "taken" bitset would reduce memory from O(nW) to O(W + n).
3. 2-opt is worth enabling when routes have more than ~10 stops (≈ 8 % → 0.3 % above optimal for small cases).
4. **Deadline limitation (observed).** Nearest neighbour minimises distance and ignores deadlines. On the large dataset with `--all-trips`, 7 of 11 trips contained at least one parcel whose ETA exceeded its deadline (each trip is also assumed to start at t = 0). A deadline-aware route (e.g. insert stops by deadline, or penalise lateness in 2-opt) is the main future improvement.
5. Parcels are assigned to trips greedily; a bin-packing/vehicle-routing formulation could balance trips better.

# 5. Phase 5 – Demonstration and results

How to run: see `README.md`. Console traces for each dataset are saved in `outputs/`.

![Medium dataset with 2-opt](../outputs/screenshot_run_medium_2opt.png)

*Medium dataset:* nearest neighbour 150.3 km; with `--two-opt` 148.2 km.

![Large dataset, all trips](../outputs/screenshot_run_large_all_trips.png)

*Large dataset:* all 200 parcels delivered in 11 trips, 2398.9 km in total.

![Unit tests](../outputs/screenshot_test_results.png){width=70%}

**Complexity summary.**

| Stage | Time | Space |
|---|---|---|
| Merge sort | O(n log n) | O(n) |
| Knapsack DP | O(n·W) | O(n·W) |
| Dijkstra × k | O(k (V+E) log V) | O(V + k²) |
| Nearest neighbour | O(k²) | O(k²) |
| 2-opt | O(k²) per pass | O(k) |

**Conclusion.** The four techniques combine into a working planner that loads the most valuable parcels, computes real road distances, and produces a short delivery route. Measured runtimes agree with the theoretical complexities, DP is provably optimal where greedy is not, and the 2-opt experiment shows how an approximation can be quantified against the exact optimum.
