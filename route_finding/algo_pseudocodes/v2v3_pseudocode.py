"""

Pseudocode for the route finding algorithm used for
the actual 11- and 24-hour runs. It's a big improvement
upon v0v1, but still imperfect by far. Enjoy!


===== V2/3: Explore Set =====

== Global constants:
- min_transfer_time (2 (minutes))
- max_transfer_time (30 (minutes))
- duration (11 / 24 (hours))

== Initiation parameters:
- start_time (08:00 / 00:04)
- start_station (Ehv / Mp)

-> Initialize algorithm with settings by running
    explore_set = ExploreSet(run_path=run_path)


=== algorithm run_explore_set(State)
== Procedure:
1. Set initial State
   a. Initialize PriorityQueue (min-heap; (-State.score, State))
2. Explore initial State (starting conditions)
3. Add possible transfers to PriorityQueue (see filter_timetable())
4. While the PriorityQueue is not empty, or until manual termination:
   a. Explore best State (lowest value -State.score, ergo highest actual score)
   b. Add possible transfers to PriorityQueue (see filter_timetable())
   c. Update PriorityQueue (restore min-heap properties)

"""
