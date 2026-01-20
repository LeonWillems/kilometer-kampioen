"""
This file will contain a class to calculate distances between stations that
are not direct neighbors.

Some context:
- There exists a table with 'tariff units', that does not correlate one-to-one
    with the distances used by Kilometer Kampioen.
- There does exist a file with distances between neighboring stations.
- The above will work for sprinters, but not for intercity trains that
    travel through multiple stations.
- Thus, when encountering a new pair (example 'Ht' -> 'Ehv'), find and add
    this distance to the station_distances.

How?
- We will use Dijkstra's Algorithm to find a direct path between
    two stations, which is the shortest in terms of distance travelled.

Pseudocode for Dijkstra:
- Input:
    - A graph G (an adjacency list with distances)
    - The starting vertex root of G (a station)
- Output: Given a goal vertex, the shortest path & distance from the root

First, initialize some data structures:
 1  procedure Initialization(G, root):
 2      for each vertex v in G:
 3          dist[v] <- infinity
 4          parent[v] <- undefined
 5          add v to queue Q
 6      dist[root] = 0

To find the paths to all vertices from some root:
 1  procedure Dijkstra(G, root):
 2      while Q is not empty do
 3          v := v in Q with minimum dist[v]
 4          Q.remove(v)
 5
 6          for each edge (v, u) where v in Q and u is a direct neighbor of v:
 7              new_dist := dist[v] + d(v, u) (in G)
 8              if new_dist < dist[u]:
 9                  dist[u] := new_dist

To find the shortest path from root to some goal:
 1  procedure Search(root, goal):
 2      path := empty sequence
 3      u := goal
 4
 5      if prev[u] is defined or u == root:
 6          while u is defined:
 7              path.insert(u) (insert at start)
 8              u := prev[u]
"""

from numpy import inf
from copy import deepcopy


class Dijkstra:
    def __init__(self, adjacency_list: dict[str, dict[str, float]]):
        """Only need the grap G, represented as an adjacency list
        with distances.

        Args:
        - adjacency_list (dict): A dictionary where keys are station names and
            values are dictionaries of neighboring stations with
            their distances.
            Example: {"Bhv": {"Utm": 6.2, "Uto": 5.6, "Dld": 2.9}, ...}

        Attributes:
        - nodes (list): The keys of the graph, example: ['Bhv', 'Ehv', ...]
        """
        self.graph = adjacency_list
        self.nodes = list(self.graph)

    def _init_data_structures(self, start: str):
        """When constructing paths, start with fresh data structures.

        Args:
        - start (str): Starting node, or the root. Example 'b'

        Attributes (in this example, the start is 'b'):
        - dists (dict): Distances from start to each node, example
            before: {'a': inf, 'b': 0, ...}, after: {'a': 4, 'b': 0, ...}
        - parents (dict): Predecessor (parent) of each node, example
            before: {'a': None, 'b': None, ...},
            after: {'a': 'b', 'b': None, ...}
        - queue (list): Queue of the nodes to still process,
            example ['a', 'b', ...]
        """
        self.start = start

        self.dists = {node: inf for node in self.nodes}
        self.dists[self.start] = 0  # Starting node gets distance 0

        self.parents = {node: None for node in self.nodes}
        self.queue = deepcopy(self.nodes)

    def _get_min_dist(self) -> str:
        """Gets the node in the `queue` with the minimum distance in `dists`.
        First, initialize the distance for each node in queue. Then, find the
        minimum. Lastly, deleted the found node from the queue.
        """
        queue_dists = {node: self.dists[node] for node in self.queue}
        min_dist_node = min(queue_dists, key=queue_dists.get)
        self.queue.remove(min_dist_node)
        return min_dist_node

    def construct_paths(self, start: str):
        """Given a start node, will invoke Dijkstra's Algorithm for
        calculate distances of shortest paths to each other node,
        keeping track of each node's parent node.

        Args:
        - start (str): Starting node, or the root. Example 'b'
        """
        self._init_data_structures(start)

        while self.queue:
            current = self._get_min_dist()

            for neighbor, dist in self.graph[current].items():
                new_dist_current = self.dists[current] + dist

                if new_dist_current < self.dists[neighbor]:
                    self.dists[neighbor] = new_dist_current
                    self.parents[neighbor] = current

    def _find_shortest_path(self, goal: str) -> list[str]:
        """Find the shortest path from the start node to the goal node.

        Args:
        - start (str): Example 'b'
        - goal (str): Example 'g'

        Returns:
        - list[str]: Path of nodes visited, example ['b', 'a', 'g']. Always
            includes both the start and the goal nodes.
        """
        path = []
        parent = goal

        if goal in self.parents or self.start == parent:
            while parent in self.parents:
                path.insert(0, parent)
                parent = self.parents[parent]

        return path

    def search(self, goal: str) -> tuple[list[str], float]:
        """Given a goal node, finds the shortest path by backtraking, returns
        this path and the distance.

        Args:
        - start (str): Example 'b'
        - goal (str): Example 'g'

        Returns:
        - tuple[list[str], float]: Shortest path and its distance, example
            (['b', 'a', 'g'], 6)
        """
        shortest_path = self._find_shortest_path(goal)
        return shortest_path, self.dists[goal]


if __name__ == "__main__":
    # Example usage to find the shortest path between 'a' and 'i'
    distances = {
        'a': {'b': 1, 'f': 2},
        'b': {'a': 1, 'c': 1},
        'c': {'b': 1, 'd': 1},
        'd': {'c': 1, 'e': 1},
        'e': {'d': 1, 'g': 2, 'h': 1},
        'f': {'a': 2, 'g': 2},
        'g': {'e': 2, 'f': 2},
        'h': {'e': 1, 'i': 1},
        'i': {'h': 1},
    }

    start, goal = 'a', 'i'

    dijkstra = Dijkstra(adjacency_list=distances)
    dijkstra.construct_paths(start)

    # If we fix the start and run the above, we can run the line below
    # for each possible goal to quickly find the distance
    path, distance = dijkstra.search(goal)

    print(f"Path found: {path}")
    print(f"With distance: {distance}")
