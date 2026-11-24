"""Run with:  python -m unittest discover tests -v"""
import itertools, random, unittest
from courier.models import Parcel
from courier.sorting import merge_sort, insertion_sort, builtin_sort
from courier.knapsack import knapsack_dp, knapsack_greedy
from courier.graph import build_graph, dijkstra, path_to
from courier.tsp import distance_matrix, nearest_neighbour, tour_length, two_opt, brute_force
from courier.datagen import make_problem
from courier.planner import plan_trip, plan_all_trips


def rand_parcels(n, seed):
    r = random.Random(seed)
    return [Parcel(i, r.randint(1, 15), r.randint(1, 5), r.randint(1, 24), 1) for i in range(n)]


class TestSorting(unittest.TestCase):
    def test_matches_builtin(self):
        for s in range(20):
            ps = rand_parcels(30, s)
            self.assertEqual(merge_sort(ps), builtin_sort(ps))
            self.assertEqual(insertion_sort(ps), builtin_sort(ps))

    def test_edge_cases(self):
        self.assertEqual(merge_sort([]), [])
        p = rand_parcels(1, 0)
        self.assertEqual(merge_sort(p), p)

    def test_deadline_then_priority(self):
        a, b = Parcel(1, 1, 1, 5, 1), Parcel(2, 1, 5, 5, 1)
        self.assertEqual([x.pid for x in merge_sort([a, b])], [2, 1])


class TestKnapsack(unittest.TestCase):
    def test_optimal_vs_bruteforce(self):
        for s in range(30):
            ps, cap = rand_parcels(9, s), 30
            best = 0
            for mask in range(1 << len(ps)):
                sel = [ps[i] for i in range(len(ps)) if mask >> i & 1]
                if sum(x.weight for x in sel) <= cap:
                    best = max(best, sum(x.value for x in sel))
            chosen, val, _ = knapsack_dp(ps, cap)
            self.assertEqual(val, best)
            self.assertEqual(sum(x.value for x in chosen), val)
            self.assertLessEqual(sum(x.weight for x in chosen), cap)

    def test_dp_never_worse_than_greedy(self):
        for s in range(30):
            ps = rand_parcels(15, s)
            self.assertGreaterEqual(knapsack_dp(ps, 40)[1], knapsack_greedy(ps, 40)[1])

    def test_zero_capacity(self):
        self.assertEqual(knapsack_dp(rand_parcels(5, 1), 0)[1], 0)


class TestGraph(unittest.TestCase):
    def test_known_graph(self):
        adj = build_graph(5, [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5)])
        dist, prev = dijkstra(adj, 0)
        self.assertEqual(dist[:4], [0, 3, 1, 4])
        self.assertEqual(path_to(prev, 0, 3), [0, 2, 1, 3])
        self.assertEqual(dist[4], float("inf"))     # unreachable node

    def test_against_floyd_warshall(self):
        p = make_problem(25, 1, 10, seed=3)
        n, INF = p.n_nodes, float("inf")
        fw = [[0 if i == j else INF for j in range(n)] for i in range(n)]
        for u, v, w in p.edges:
            fw[u][v] = fw[v][u] = min(fw[u][v], w)
        for k, i, j in itertools.product(range(n), repeat=3):
            fw[i][j] = min(fw[i][j], fw[i][k] + fw[k][j])
        dist, _ = dijkstra(build_graph(n, p.edges), 0)
        for j in range(n):
            self.assertAlmostEqual(dist[j], fw[0][j])


class TestTSP(unittest.TestCase):
    def setUp(self):
        self.p = make_problem(30, 1, 10, seed=5)
        self.adj = build_graph(self.p.n_nodes, self.p.edges)
        self.stops = [0, 4, 9, 13, 17, 22, 28]
        self.D, _ = distance_matrix(self.adj, self.stops)

    def test_tour_valid(self):
        t = nearest_neighbour(self.D, 0, self.stops)
        self.assertEqual(t[0], 0); self.assertEqual(t[-1], 0)
        self.assertEqual(sorted(t[:-1]), sorted(self.stops))

    def test_quality_ordering(self):
        nn = nearest_neighbour(self.D, 0, self.stops)
        opt = brute_force(self.D, 0, self.stops)[1]
        self.assertLessEqual(tour_length(self.D, two_opt(self.D, nn)), tour_length(self.D, nn) + 1e-9)
        self.assertLessEqual(opt, tour_length(self.D, two_opt(self.D, nn)) + 1e-9)


class TestPlanner(unittest.TestCase):
    def test_trip_respects_capacity(self):
        p = make_problem(40, 30, 80, seed=2)
        t = plan_trip(p)
        self.assertLessEqual(t["load"], p.capacity)
        self.assertEqual(t["full_route"][0], p.depot); self.assertEqual(t["full_route"][-1], p.depot)

    def test_all_trips_cover_every_parcel_once(self):
        p = make_problem(40, 30, 80, seed=2)
        ids = [x.pid for t in plan_all_trips(p) for x in t["chosen"]]
        self.assertEqual(sorted(ids), sorted(x.pid for x in p.parcels))


if __name__ == "__main__":
    unittest.main()
