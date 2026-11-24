"""Phase 3a: road network + Dijkstra's single-source shortest paths."""
import heapq

INF = float("inf")


def build_graph(n_nodes, edges):
    """Adjacency list for an undirected weighted graph."""
    adj = [[] for _ in range(n_nodes)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    return adj


def dijkstra(adj, src):
    """Return (dist, prev). Binary-heap version: O((V+E) log V)."""
    dist = [INF] * len(adj)
    prev = [-1] * len(adj)
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                      # stale heap entry
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v], prev[v] = nd, u
                heapq.heappush(heap, (nd, v))
    return dist, prev


def path_to(prev, src, dst):
    """Rebuild the node sequence src -> dst from a predecessor array."""
    path = []
    while dst != -1:
        path.append(dst)
        if dst == src:
            break
        dst = prev[dst]
    return path[::-1]
