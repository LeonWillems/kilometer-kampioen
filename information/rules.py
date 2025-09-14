"""

RULES FOR THE KILOMETER-KAMPIOEN COMPETITION

- 24-hour version: Start between 00:00 and 04:00
- 12:hour version: Start between 00:00 and 12:00
- In both cases: visit station Zwolle between 11:00 and 15:00 for a stamp

Counting a connection:
- A connection is a direct route between two stations
- Every connection can be counted at most twice

- If a connection is to be counted twice, need to stop at all
    intermediate stations for at least one of the journeys. Examples:
    - If you drive with the intercity from Eindhoven to 's-Hertogenosch,
        and then back with the sprinter (stopping at all station) can count
        the connection Ehv - Ht twice
    - If you take the intercity Ehv - Ht, and then the intercity Ht - Ehv,
        can only count once (did not stop everywhere)
    - You can take the intercity Til - Ht and then the intercity Ht - Til,
        as there are no inbetween stations, so count twice. Can ofcourse also
        take the sprinter once or twice
        
- To make communication a bit easier, the Kilometer Kampioen organisation
    regards a 'traject' as a route from one intersection to the next
    - So, Vlissingen - Roosendaal is one 'traject' but consists of many
        intermediate stations

See `scorekaart2023.xlsx` for details on distances and stuff.

"""