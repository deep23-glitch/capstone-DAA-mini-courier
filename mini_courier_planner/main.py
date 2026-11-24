"""Mini-Courier Planner - command line entry point.

Usage:
    python main.py data/small.json                # one trip
    python main.py data/medium.json --two-opt     # add 2-opt improvement
    python main.py data/large.json --all-trips    # plan until every parcel is assigned
"""
import argparse
from courier.models import load_problem
from courier.planner import plan_trip, plan_all_trips
from courier.sorting import merge_sort


def show_trip(problem, t, n=1):
    name = lambda i: problem.names.get(i, f"Node {i}")
    print(f"\n{'=' * 70}\nTRIP {n}\n{'=' * 70}")
    if n == 1:
        print("\n[1] PARCELS SORTED (deadline asc, priority desc) - top 10")
        print(f"    {'ID':>4} {'Wt':>3} {'Pri':>3} {'DL(h)':>5} {'Dest':>5} {'Value':>5}")
        for p in t["ordered"][:10]:
            print(f"    {p.pid:>4} {p.weight:>3} {p.priority:>3} {p.deadline:>5} {p.destination:>5} {p.value:>5}")
    print(f"\n[2] KNAPSACK: loaded {len(t['chosen'])} parcels, "
          f"{t['load']}/{problem.capacity} kg, total value {t['value']}")
    print("    parcel ids:", sorted(p.pid for p in t["chosen"]))
    print("\n[3] DELIVERY ORDER (nearest neighbour)")
    for a, b in zip(t["tour"], t["tour"][1:]):
        eta = t["etas"].get(b)
        print(f"    {name(a)} -> {name(b)}: {t['D'][(a, b)]:.1f} km" + (f"  (ETA {eta:.2f} h)" if b != problem.depot else "  (return)"))
    print(f"    Total route length: {t['km']:.1f} km")
    r = t["full_route"]
    print(f"    Full road path ({len(r)} nodes): {' > '.join(map(str, r[:25]))}{' ...' if len(r) > 25 else ''}")
    print(f"    Late parcels: {[p.pid for p in t['late']] or 'none'}")
    print("\n[4] STAGE RUNTIMES (ms): " + ", ".join(f"{k}={v * 1000:.3f}" for k, v in t["timings"].items()))


def main():
    ap = argparse.ArgumentParser(description="Mini-Courier Planner")
    ap.add_argument("dataset")
    ap.add_argument("--two-opt", action="store_true", help="improve the tour with 2-opt")
    ap.add_argument("--all-trips", action="store_true", help="plan repeated trips for all parcels")
    a = ap.parse_args()
    pr = load_problem(a.dataset)
    print(f"Dataset: {a.dataset} | nodes={pr.n_nodes} edges={len(pr.edges)} "
          f"parcels={len(pr.parcels)} capacity={pr.capacity} kg")
    if a.all_trips:
        trips = plan_all_trips(pr, a.two_opt)
        for i, t in enumerate(trips, 1):
            show_trip(pr, t, i)
        print(f"\nSUMMARY: {len(trips)} trips, {sum(t['km'] for t in trips):.1f} km total, "
              f"{sum(len(t['chosen']) for t in trips)} parcels delivered")
    else:
        show_trip(pr, plan_trip(pr, use_two_opt=a.two_opt))


if __name__ == "__main__":
    main()
