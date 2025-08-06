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
- We will use breadth-first search (BFS) to find a direct path between two stations.

Pseudocode for BFS:
- Input: 
    - A graph G (an adjacency list with distances)
    - The starting vertex root of G (a station)
- Output: Goal state. The parent links trace the shortest path back to root

 1  procedure BFS(G, root):
 2      let Q be a queue
 3      label root as explored
 4      Q.enqueue(root)
 5      while Q is not empty do
 6          v := Q.dequeue()
 7          if v is the goal then
 8              return v
 9          for all edges from v to w in G.adjacentEdges(v) do
10              if w is not labeled as explored then
11                  label w as explored
12                  w.parent := v
13                  Q.enqueue(w)

Important to note! BFS will not actually find the shortest distance for any graph,
but it will find a direct path with least nodes. For now, that is fine. For later,
check whether this is still the way to go for our train network, as a counter-example
might exist. If latter, implement Dijkstra's algorithm instead.
"""


class BFS:
    def __init__(self, adjacency_list: dict[str, dict[str, float]]):
        """Only need the grap G, represented as an adjacency list with distances.
        
        Args:
        - adjacency_list (dict): A dictionary where keys are station names and 
            values are dictionaries of neighboring stations with their distances.
            Example: {"Bhv": {"Utm": 6.2, "Uto": 5.6, "Dld": 2.9}, ...}
        """
        self.graph = adjacency_list

    def _reconstruct_path(self, parent: dict[str, str], goal: str):
        """Reconstruct the path from start to goal using parent links.
        In other words, backwards tracing from goal to start.
        
        Args:
        - parent (dict): A dictionary mapping each node to its parent in 
            the BFS tree
        - goal (str): The goal node to reconstruct the path to
        """
        path = []
        total_distance = 0.0  # Keep track of distance travelled
        
        while goal is not None:
            path.append(goal)
            goal = parent[goal]
            total_distance += self.graph.get(goal, {}).get(path[-1], 0.0)

        return path[::-1], total_distance  # Return reversed path & distance

    def search(self, start: str, goal: str) -> tuple[list, float]:
        """Perform BFS to find the shortest path from start to goal.
        
        Args:
        - start (str): The starting station
        - goal (str): The destination station
        
        Returns:
        - tuple: A tuple containing the path as a list of station names and
            the total distance as a float. If no path is found, returns ([], 0.0)
        """
        queue = [start]
        visited = {start}
        parent = {start: None}

        # Evaluate all nodes, or find the goal node and terminate
        while queue:
            current = queue.pop(0)  # Dequeue the first element

            if current == goal:  # Shortest path found
                return self._reconstruct_path(parent, goal)

            for neighbor in self.graph.get(current, {}):
                # Only enqueue unvisited neighbors
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        return [], 0.0  # No path found

