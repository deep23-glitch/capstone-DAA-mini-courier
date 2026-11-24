# Mini-Courier Planner
Capstone Assignment – Design & Analysis of Algorithms (ETCCDA302), K.R. Mangalam University

Author: Deep Saha (Roll no. 2501010058)

Given a list of parcels and a road network, the planner (1) sorts parcels by urgency, (2) picks the
most valuable set that fits in the van (0/1 knapsack DP), (3) finds true road distances (Dijkstra),
and (4) orders the stops with a nearest-neighbour TSP approximation (optional 2-opt refinement).

## Project layout
```
main.py                 CLI entry point
benchmark.py            Phase 4 experiments -> outputs/*.csv, chart_*.png
make_screenshots.py     renders console traces into outputs/screenshot_*.png
courier/
  models.py             Parcel, Problem, JSON load/save
  sorting.py            merge sort (main), insertion sort + Timsort (comparison)
  knapsack.py           0/1 knapsack DP with backtracking, greedy baseline
  graph.py              adjacency list + Dijkstra (binary heap)
  tsp.py                distance matrix, nearest neighbour, 2-opt, brute force, route expansion
  planner.py            integrates all stages, times each, ETA/late check, multi-trip planning
  datagen.py            seeded dataset generator
data/                   small.json (12 nodes, 10 parcels), medium.json (60/40), large.json (300/200)
tests/test_all.py       12 unit tests
outputs/                run traces, charts, CSVs, screenshots
docs/REPORT.docx        final report (source: REPORT.md)
```

## How to run (Python 3.8+; only matplotlib needed, and only for charts)
```bash
pip install matplotlib
python -m courier.datagen                    # (re)generate datasets in data/
python main.py data/small.json               # plan one trip
python main.py data/medium.json --two-opt    # with 2-opt route improvement
python main.py data/large.json --all-trips   # keep planning trips until all parcels are assigned
python -m unittest discover tests -v         # run the tests
python benchmark.py                          # runtime experiments + charts
python make_screenshots.py                   # terminal-style screenshots
```

## Dataset format (JSON)
`depot`, `capacity` (kg), `speed_kmph`, `n_nodes`, `edges` as `[u, v, km]`, `names` (optional),
`parcels` as `{pid, weight, priority 1-5, deadline (hours), destination (node id)}`.
You can run it on your own file in this format.

## Complexity summary
| Stage | Algorithm | Time | Space |
|---|---|---|---|
| Prioritise | Merge sort | O(n log n) | O(n) |
| Pack | 0/1 knapsack DP | O(n·W) | O(n·W) |
| Distances | Dijkstra × k stops | O(k (V+E) log V) | O(V + k²) |
| Route | Nearest neighbour | O(k²) | O(k²) |
| Route (opt.) | 2-opt | O(k²) per pass | O(k) |
