"""Data models and dataset loading (Phase 1: data design)."""
from dataclasses import dataclass
import json


@dataclass(frozen=True)
class Parcel:
    pid: int            # unique parcel id
    weight: int         # kg (integer so the knapsack DP table can index by it)
    priority: int       # 1 (low) .. 5 (critical)
    deadline: int       # hours from start of day by which it must be delivered
    destination: int    # graph node id of the delivery point

    @property
    def value(self) -> int:
        """Benefit of loading this parcel on the current trip.

        Higher priority and tighter deadlines are worth more, so the knapsack
        prefers urgent parcels when the van cannot carry everything.
        """
        urgency_bonus = max(0, 12 - self.deadline)   # deadline within 12h -> bonus
        return self.priority * 10 + urgency_bonus


@dataclass
class Problem:
    depot: int
    capacity: int
    speed_kmph: float
    n_nodes: int
    edges: list          # [(u, v, km), ...] undirected road segments
    parcels: list        # [Parcel, ...]
    names: dict          # node id -> label


def load_problem(path: str) -> Problem:
    with open(path) as f:
        d = json.load(f)
    parcels = [Parcel(**p) for p in d["parcels"]]
    names = {int(k): v for k, v in d.get("names", {}).items()}
    return Problem(
        depot=d["depot"], capacity=d["capacity"], speed_kmph=d.get("speed_kmph", 30),
        n_nodes=d["n_nodes"], edges=[tuple(e) for e in d["edges"]],
        parcels=parcels, names=names,
    )


def save_problem(p: Problem, path: str) -> None:
    d = {
        "depot": p.depot, "capacity": p.capacity, "speed_kmph": p.speed_kmph,
        "n_nodes": p.n_nodes, "edges": [list(e) for e in p.edges],
        "names": {str(k): v for k, v in p.names.items()},
        "parcels": [dict(pid=x.pid, weight=x.weight, priority=x.priority,
                         deadline=x.deadline, destination=x.destination)
                    for x in p.parcels],
    }
    with open(path, "w") as f:
        json.dump(d, f, indent=1)
