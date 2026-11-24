"""Phase 4: runtime + quality experiments. Writes CSVs and PNG charts to outputs/.

Run:  python benchmark.py
"""
import csv, os, random, time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from courier.models import Parcel, load_problem
from courier.sorting import merge_sort, insertion_sort, builtin_sort
from courier.knapsack import knapsack_dp, knapsack_greedy
from courier.graph import build_graph, dijkstra
from courier.tsp import distance_matrix, nearest_neighbour, two_opt, tour_length, brute_force
from courier.datagen import make_problem
from courier.planner import plan_trip

OUT = "outputs"
os.makedirs(OUT, exist_ok=True)
C = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed"]


def best_of(fn, reps=3):
    """Minimum wall time (seconds) over `reps` runs - reduces timing noise."""
    best = float("inf")
    for _ in range(reps):
        t = time.perf_counter(); fn(); best = min(best, time.perf_counter() - t)
    return best


def parcels(n, seed=0):
    r = random.Random(seed)
    return [Parcel(i, r.randint(2, 25), r.randint(1, 5), r.randint(2, 24), 1) for i in range(n)]


def write_csv(name, header, rows):
    with open(f"{OUT}/{name}.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)


def style(ax, title, xl, yl, log=False):
    ax.set_title(title, fontsize=11, fontweight="bold"); ax.set_xlabel(xl); ax.set_ylabel(yl)
    ax.grid(alpha=.3)
    if log: ax.set_xscale("log"); ax.set_yscale("log")
    ax.legend(frameon=False)


def exp_sorting():
    ns = [100, 200, 400, 800, 1600, 3200]
    rows = []
    for n in ns:
        ps = parcels(n)
        rows.append([n] + [best_of(lambda f=f: f(ps)) * 1000 for f in (merge_sort, insertion_sort, builtin_sort)])
    write_csv("sorting_runtime", ["n", "merge_ms", "insertion_ms", "timsort_ms"], rows)
    fig, ax = plt.subplots(figsize=(6, 4))
    for i, lbl in enumerate(["Merge sort O(n log n)", "Insertion sort O(n²)", "Python sorted (Timsort)"]):
        ax.plot(ns, [r[i + 1] for r in rows], "o-", color=C[i], label=lbl)
    style(ax, "Parcel sorting runtime", "number of parcels n", "time (ms)", log=True)
    fig.tight_layout(); fig.savefig(f"{OUT}/chart_sorting.png", dpi=150); plt.close(fig)
    return rows


def exp_knapsack():
    ns = [50, 100, 200, 400, 800]
    rows_n = [[n, best_of(lambda: knapsack_dp(parcels(n), 200), 2) * 1000] for n in ns]
    Ws = [100, 200, 400, 800, 1600]
    rows_w = [[W, best_of(lambda: knapsack_dp(parcels(200), W), 2) * 1000] for W in Ws]
    write_csv("knapsack_vs_n", ["n", "ms"], rows_n); write_csv("knapsack_vs_W", ["W", "ms"], rows_w)
    # DP vs greedy value gap
    gaps = []
    for s in range(200):
        ps = parcels(15, s); cap = 60
        gaps.append((knapsack_dp(ps, cap)[1], knapsack_greedy(ps, cap)[1]))
    worse = sum(1 for d, g in gaps if g < d)
    avg_loss = sum((d - g) / d for d, g in gaps) / len(gaps) * 100
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    axs[0].plot(ns, [r[1] for r in rows_n], "o-", color=C[0], label="W = 200 fixed")
    style(axs[0], "Knapsack DP vs number of parcels", "n", "time (ms)")
    axs[1].plot(Ws, [r[1] for r in rows_w], "o-", color=C[1], label="n = 200 fixed")
    style(axs[1], "Knapsack DP vs capacity", "capacity W (kg)", "time (ms)")
    fig.tight_layout(); fig.savefig(f"{OUT}/chart_knapsack.png", dpi=150); plt.close(fig)
    return rows_n, rows_w, worse, avg_loss, len(gaps)


def exp_dijkstra():
    Vs = [100, 200, 400, 800, 1600]
    rows = []
    for V in Vs:
        p = make_problem(V, 1, 10, seed=V)
        adj = build_graph(V, p.edges)
        rows.append([V, len(p.edges), best_of(lambda: dijkstra(adj, 0)) * 1000])
    write_csv("dijkstra_runtime", ["V", "E", "ms"], rows)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(Vs, [r[2] for r in rows], "o-", color=C[2], label="Dijkstra (binary heap)")
    style(ax, "Single-source Dijkstra runtime", "nodes V (E ≈ 3V)", "time (ms)")
    fig.tight_layout(); fig.savefig(f"{OUT}/chart_dijkstra.png", dpi=150); plt.close(fig)
    return rows


def exp_tsp():
    p = make_problem(300, 1, 10, seed=99); adj = build_graph(300, p.edges)
    ks = [10, 20, 40, 80, 160]
    rows = []
    for k in ks:
        stops = [0] + random.Random(k).sample(range(1, 300), k - 1)
        D, _ = distance_matrix(adj, stops)
        nn = nearest_neighbour(D, 0, stops)
        t_nn = best_of(lambda: nearest_neighbour(D, 0, stops)) * 1000
        t_2 = best_of(lambda: two_opt(D, nn), 1) * 1000
        opt2 = two_opt(D, nn)
        rows.append([k, tour_length(D, nn), tour_length(D, opt2), t_nn, t_2])
    write_csv("tsp_scaling", ["k_stops", "nn_km", "2opt_km", "nn_ms", "2opt_ms"], rows)
    # quality vs exact optimum on small instances
    ratios_nn, ratios_2 = [], []
    for s in range(30):
        stops = [0] + random.Random(s).sample(range(1, 300), 7)
        D, _ = distance_matrix(adj, stops)
        nn = nearest_neighbour(D, 0, stops)
        opt = brute_force(D, 0, stops)[1]
        ratios_nn.append(tour_length(D, nn) / opt); ratios_2.append(tour_length(D, two_opt(D, nn)) / opt)
    q = dict(nn_avg=sum(ratios_nn) / 30, nn_max=max(ratios_nn), t2_avg=sum(ratios_2) / 30, t2_max=max(ratios_2))
    write_csv("tsp_quality", ["metric", "value"], list(q.items()))
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    axs[0].plot(ks, [r[1] for r in rows], "o-", color=C[0], label="Nearest neighbour")
    axs[0].plot(ks, [r[2] for r in rows], "s-", color=C[2], label="NN + 2-opt")
    style(axs[0], "Route length vs stops", "stops k", "route length (km)")
    axs[1].plot(ks, [r[3] for r in rows], "o-", color=C[0], label="Nearest neighbour")
    axs[1].plot(ks, [r[4] for r in rows], "s-", color=C[2], label="2-opt refinement")
    style(axs[1], "TSP step runtime", "stops k", "time (ms)", log=True)
    fig.tight_layout(); fig.savefig(f"{OUT}/chart_tsp.png", dpi=150); plt.close(fig)
    return rows, q


def exp_pipeline():
    rows = []
    for name in ("small", "medium", "large"):
        pr = load_problem(f"data/{name}.json")
        best = None
        for _ in range(3):
            t = plan_trip(pr)["timings"]
            best = t if best is None else {k: min(best[k], t[k]) for k in t}
        rows.append([name, pr.n_nodes, len(pr.parcels)] + [best[k] * 1000 for k in ("sort", "knapsack", "dijkstra", "tsp")])
    write_csv("pipeline_runtime", ["dataset", "nodes", "parcels", "sort_ms", "knapsack_ms", "dijkstra_ms", "tsp_ms"], rows)
    fig, ax = plt.subplots(figsize=(7, 4))
    bottom = [0] * len(rows)
    for i, (k, lbl) in enumerate(zip(range(3, 7), ["Sorting", "Knapsack DP", "Dijkstra", "TSP (NN)"])):
        vals = [r[k] for r in rows]
        ax.bar([r[0] for r in rows], vals, bottom=bottom, color=C[i], label=lbl)
        bottom = [b + v for b, v in zip(bottom, vals)]
    style(ax, "End-to-end trip planning time by dataset", "dataset", "time (ms)")
    fig.tight_layout(); fig.savefig(f"{OUT}/chart_pipeline.png", dpi=150); plt.close(fig)
    return rows


if __name__ == "__main__":
    s = exp_sorting(); kn, kw, worse, loss, tot = exp_knapsack(); d = exp_dijkstra(); t, q = exp_tsp(); pl = exp_pipeline()
    lines = ["BENCHMARK SUMMARY", "-" * 60,
             "Sorting n=3200 (ms): merge=%.2f insertion=%.2f timsort=%.2f" % tuple(s[-1][1:]),
             "Knapsack n=800,W=200: %.1f ms | n=200,W=1600: %.1f ms" % (kn[-1][1], kw[-1][1]),
             f"DP beat greedy in {worse}/{tot} random instances; greedy lost {loss:.1f}% value on average",
             "Dijkstra V=1600: %.2f ms" % d[-1][2],
             "TSP k=160: NN=%.0f km (%.1f ms) -> 2-opt=%.0f km (%.1f ms)" % (t[-1][1], t[-1][3], t[-1][2], t[-1][4]),
             "TSP quality vs exact optimum (k=8, 30 trials): NN avg %.3fx max %.3fx | 2-opt avg %.3fx max %.3fx"
             % (q["nn_avg"], q["nn_max"], q["t2_avg"], q["t2_max"]),
             "Pipeline (ms): " + "; ".join(f"{r[0]} sort={r[3]:.2f} knap={r[4]:.2f} dij={r[5]:.2f} tsp={r[6]:.2f}" for r in pl)]
    open(f"{OUT}/benchmark_summary.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
