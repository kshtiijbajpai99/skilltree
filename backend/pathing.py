"""
Orders the "missing prerequisites" subgraph returned by
queries.get_missing_prereq_subgraph into a valid learning sequence.

The graph query does the hard part (finding, at arbitrary depth, exactly
which skills still stand between the learner and their target). Turning
that subgraph into a single linear order is a plain topological sort, so
it's done here in Python rather than as a wall of Cypher.
"""

from collections import defaultdict, deque


def build_learning_path(nodes: list[dict], edges: list[dict]) -> list[dict]:
    if not nodes:
        return []

    by_id = {n["id"]: n for n in nodes}
    indegree = {n["id"]: 0 for n in nodes}
    adjacency = defaultdict(list)

    for edge in edges:
        src, dst = edge["source"], edge["target"]
        if src not in by_id or dst not in by_id:
            continue
        adjacency[src].append(dst)
        indegree[dst] += 1

    # Stable order: process ready nodes sorted by category then name, so the
    # output reads sensibly rather than in arbitrary queue order.
    ready = deque(
        sorted(
            [nid for nid, deg in indegree.items() if deg == 0],
            key=lambda nid: (by_id[nid]["category"], by_id[nid]["name"]),
        )
    )

    ordered = []
    seen = set()
    while ready:
        current = ready.popleft()
        if current in seen:
            continue
        seen.add(current)
        ordered.append(by_id[current])
        newly_ready = []
        for neighbor in adjacency[current]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0 and neighbor not in seen:
                newly_ready.append(neighbor)
        newly_ready.sort(key=lambda nid: (by_id[nid]["category"], by_id[nid]["name"]))
        for n in newly_ready:
            ready.append(n)

    if len(ordered) != len(nodes):
        raise ValueError(
            "Could not resolve a valid learning order — the prerequisite "
            "graph for this skill appears to contain a cycle."
        )

    return ordered
