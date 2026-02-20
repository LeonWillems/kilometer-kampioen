
"""

Pseudocode for the route finding algorithm.
Beware that many details are omitted. This
file serves the purpose of giving a rough
idea what happens under the hood. Enjoy!


===== V0: Greedy DFS =====

== Global constants:
- min_transfer_time (3 (minutes))
- max_transfer_time (15 (minutes))
- end_time (15:00)

== Initiation parameters:
- start_time (12:00)
- start_station (Ht)

-> Kick-off algorithm by running
    GreedyDFS(
        current_time = start_time,
        current_station = start_station
    )

== Important stuff t


=== algorithm GreedyDFS(..)
== Args:
- current_time (12:45)
- current_station (Tb)

== Procedure:
1. transfer_options <- run FilterTimetable(
    current_time, current_station, global constants
)
2. top_transfers <- run ScoreFunction(transfer_options)
3. For transfer in top_transfers:
   a. new_state <- copy of current_state
   b. If transfer.section_driven == 0:
      i. new_state.total_distance <- current_state.total_distance
         + transfer.distance
   c. new_state.current_time <- transfer.arrival (at new station)
   d. new_state.current_station <- transfer.to_station
   f. If new_state.total_distance > best_state.total_distance:
      i. best_state <- copy new_state
   g. GreedyDFS(current_time, current_station)


=== algorithm FilterTimetable(..)
== Args:
- current_time
- current_station
- the timetable of all trains, end time,
  min transfer time, max transfer time,
  and the ID of the previous train

== Procedure:
1. Filter on current_station
2. Take the subset such that the departure_time is between
    the current_time and current_time + max_transfer_time
3. Sort on departure_time, increasingly
4. Futher filter on the following rule:
    Either the departure_time lies between
    current_time + min_transfer_time and
    current_time + max_transfer_time, or the departure_time
    lies between current_time and current_time + max_transfer_time
    if the ID of the previous train equal the ID of the current train
5. Return the filtered & sorted timetable


=== algorithm ScoreFunction(..)
== Args:
- transfer_options (table, transfer per row)

== Procedure:
1. For transfer in transfer_options:
   a. transfer.score
        <- transfer.distance / (transfer.waiting_time + transfer.duration)
        # average speed including waiting time
   b. transfer.section_driven
        <- Indicator whether section has already been
           driven by same train type (both ways)
2. Sort transfer_options on transfer.score (decreasingly)
3. Sort transfer_options on transfer.section_driven (increasingly, 0 is good)
4. Return top 2 transfer_options


=== Functions and/or classes omitted:
== class GreedyDFS()
Main class to puzzle all the pieces together.

== class State()
Keeps track of where we are, what time it is, the route,
and all those details for the best route found so far.

== class RouteIndicator()
Keeps a matrix of what sections have been driven already,
by what kind of train.

"""
