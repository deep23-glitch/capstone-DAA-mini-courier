"""Phase 3b: overall delivery route (TSP approximation).

Dijkstra gives true road distances between delivery points (a complete
"metric closure" graph). Nearest-neighbour then builds a tour greedily in
O(k^2). It has no constant approximation guarantee in general, so we add
2-opt (optional improvement) and brute force (small k) to measure its quality.
"""
from itertools import permutations
from .graph import dijkstra, path_to


def distance_matrix(adj, stops):
    """Run Dijkstra from every stop; return matrix D and predecessor arrays."""
    D, prevs = {}, {}
    for s in stops:
        dist, prev = dijkstra(adj, s)
        prevs[s] = prev
        for t in stops:
            D[(s, t)] = dist[t]
    return D, prevs


def nearest_neighbour(D, depot, stops):
    """Greedy tour depot -> ... -> depot over `stops` (excluding depot)."""
    todo, tour, cur = set(stops) - {depot}, [depot], depot
    while todo:
        nxt = min(todo, key=lambda s: (D[(cur, s)], s))
        tour.append(nxt); todo.remove(nxt); cur = nxt
    tour.append(depot)
    return tour


def tour_length(D, tour):
    return sum(D[(a, b)] for a, b in zip(tour, tour[1:]))


def two_opt(D, tour):
    """Repeatedly reverse segments while that shortens the tour."""
    best, improved = tour[:], True
    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                a, b, c, d = best[i - 1], best[i], best[j], best[j + 1]
                if D[(a, c)] + D[(b, d)] < D[(a, b)] + D[(c, d)] - 1e-9:
                    best[i:j + 1] = reversed(best[i:j + 1])
                    improved = True
    return best


def brute_force(D, depot, stops):
    """Exact optimum, O(k!) - only for k <= ~9, used to measure the approximation."""
    others = [s for s in stops if s != depot]
    best, best_len = None, float("inf")
    for perm in permutations(others):
        t = [depot, *perm, depot]
        L = tour_length(D, t)
        if L < best_len:
            best, best_len = t, L
    return best, best_len


def expand_route(prevs, tour):
    """Turn a tour over stops into the full node-by-node road path."""
    full = [tour[0]]
    for a, b in zip(tour, tour[1:]):
        full.extend(path_to(prevs[a], a, b)[1:])
    return full
