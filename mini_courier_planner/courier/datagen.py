"""Seeded random dataset generator (connected road graph + parcels)."""
import math
import random
from .models import Parcel, Problem, save_problem

GURUGRAM = ["Depot (KRMU Sohna Rd)", "Sector 14", "Cyber Hub", "MG Road", "Sohna Chowk",
            "Golf Course Rd", "Sushant Lok", "Udyog Vihar", "DLF Phase 3", "Huda City Centre",
            "Palam Vihar", "Badshahpur"]


def make_problem(n_nodes, n_parcels, capacity, seed=1, k_near=3, names=None):
    rnd = random.Random(seed)
    pts = [(rnd.uniform(0, 30), rnd.uniform(0, 30)) for _ in range(n_nodes)]
    dist = lambda a, b: round(math.dist(pts[a], pts[b]) * 1.2 + 0.1, 1)  # 1.2 = road winding factor
    edges = set()
    # random spanning tree guarantees connectivity
    order = list(range(n_nodes)); rnd.shuffle(order)
    for i in range(1, n_nodes):
        j = min(order[:i], key=lambda x: math.dist(pts[x], pts[order[i]]))
        edges.add(tuple(sorted((order[i], j))))
    # plus k nearest neighbours so shortest paths are not trivial
    for u in range(n_nodes):
        near = sorted((v for v in range(n_nodes) if v != u), key=lambda v: math.dist(pts[u], pts[v]))
        for v in near[:k_near]:
            edges.add(tuple(sorted((u, v))))
    edges = [(u, v, dist(u, v)) for u, v in sorted(edges)]
    parcels = [Parcel(pid=i + 1, weight=rnd.randint(2, 25), priority=rnd.randint(1, 5),
                      deadline=rnd.randint(2, 24), destination=rnd.randint(1, n_nodes - 1))
               for i in range(n_parcels)]
    labels = {i: (names[i] if names and i < len(names) else f"Node {i}") for i in range(n_nodes)}
    return Problem(depot=0, capacity=capacity, speed_kmph=30, n_nodes=n_nodes,
                   edges=edges, parcels=parcels, names=labels)


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "..", "data")
    save_problem(make_problem(12, 10, 60, seed=7, names=GURUGRAM), f"{out}/small.json")
    save_problem(make_problem(60, 40, 100, seed=11), f"{out}/medium.json")
    save_problem(make_problem(300, 200, 250, seed=21), f"{out}/large.json")
    print("datasets written to", os.path.abspath(out))
