"""Integrates every stage into one trip plan, timing each step."""
import time
from .sorting import merge_sort
from .knapsack import knapsack_dp
from .graph import build_graph
from .tsp import distance_matrix, nearest_neighbour, two_opt, tour_length, expand_route


def _timed(fn, *a):
    t = time.perf_counter()
    r = fn(*a)
    return r, time.perf_counter() - t


def plan_trip(problem, parcels=None, use_two_opt=False):
    """Plan ONE trip from the given (default: all) pending parcels."""
    pending = list(problem.parcels if parcels is None else parcels)
    timings = {}
    ordered, timings["sort"] = _timed(merge_sort, pending)
    (chosen, value, _), timings["knapsack"] = _timed(knapsack_dp, ordered, problem.capacity)
    adj = build_graph(problem.n_nodes, problem.edges)
    stops = sorted({p.destination for p in chosen} | {problem.depot})
    (D, prevs), timings["dijkstra"] = _timed(distance_matrix, adj, stops)
    tour, timings["tsp"] = _timed(nearest_neighbour, D, problem.depot, stops)
    if use_two_opt:
        tour, t2 = _timed(two_opt, D, tour)
        timings["tsp"] += t2
    full = expand_route(prevs, tour)
    km = tour_length(D, tour)

    # ETA per stop (hours, driving only) -> flag late parcels
    etas, clock = {}, 0.0
    for a, b in zip(tour, tour[1:]):
        clock += D[(a, b)] / problem.speed_kmph
        etas.setdefault(b, clock)
    late = [p for p in chosen if etas[p.destination] > p.deadline]
    return dict(ordered=ordered, chosen=chosen, value=value, tour=tour,
                full_route=full, km=km, etas=etas, late=late,
                load=sum(p.weight for p in chosen), timings=timings, D=D)


def plan_all_trips(problem, use_two_opt=False):
    """Repeat trips until every parcel is assigned (parcels heavier than capacity are skipped)."""
    left = [p for p in problem.parcels if p.weight <= problem.capacity]
    trips = []
    while left:
        t = plan_trip(problem, left, use_two_opt)
        if not t["chosen"]:
            break
        ids = {p.pid for p in t["chosen"]}
        left = [p for p in left if p.pid not in ids]
        trips.append(t)
    return trips
