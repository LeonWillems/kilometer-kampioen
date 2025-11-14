# Kilometer Kampioen
Drive as many kilometers by train as possible within 24 hours - with the help of a computer

## Setup and Usage
1. Install requirements.txt
2. Navigate one level above kilometer-kampioen (`cd ..`)
3. First, process the raw timetable data by running:
   ```bash
   python -m kilometer-kampioen.data_processing.process_timetable
   ```
   This will create the necessary processed timetable files in the `data` directory.

4. Fill in some parameters in the file below and run the route finding algorithm:
   ```bash
   python -m kilometer-kampioen.run
   ```

5. After running, can do some unit tests on the final route, to check if it's compliant with all the rules (work in progress). Will automatically grab the last route for given version.
   ```bash
   python -m kilometer-kampioen.tests.route_compliance
   ```

   The main parameters in `run.py` that you can modify are:
   - `version`: Version of the timetable data (default: 'v0')
   - `start_station`: Starting station (default: 'Ht' - 's-Hertogenbosch)
   - `start_time`: Starting time (default: 12:00)
   - `end_time`: Time by which the route must be completed (default: 15:00)
   - `min_transfer_time`: Minimum transfer time in minutes (default: 3)
   - `max_transfer_time`: Maximum transfer time in minutes (default: 15)


### Output
The algorithm will create:
- Log files in `runs/logs/v0/` with detailed information about the search process
- Parameters files in `runs/parameters/v0/` containing parameters filled in by user
- Route files in `runs/routes/v0/` containing the best routes found, named with timestamp and distance in hectometers

# Sources
- Find all rules here: https://www.kilometerkampioen.nl/
- Find all station-related content here: https://en.wikipedia.org/wiki/Railway_stations_in_the_Netherlands
    - Each station has a code. For example, "Eindhoven Centraal" has "Ehv". Please find all codes in "information/station_codes_ns.csv".
    However, we will use the other file, stated below.
- Find kilometer count courtesy here: https://github.com/nanderv/trainkms
    - A written guide how to count kilometers
    - A tool for counting kilometers
    - Number of kilometers between pairs of stations ("data/distance_between_stations.json")
    - The station codes as well, found in "information/station_codes.json". All of the distance pairs' codes are found in this file.

# V0
## Data (see "data/v0/" files)
- Intercity stations: 's-Hertogenbosch, Tilburg, Eindhoven Centraal
- Other stations: Vught, Boxtel, Best, Oisterwijk, Eindhoven Strijp-S
- Timeframe: Saturday, 12:00 - 15:00
- Actual train times for Saturday August 2nd, 2025

## Algorithm
- Implementation: Greedy Depth-First Search
- Scoring function: counted_distance/(waiting_time + travel_time)
  - counted_distance is determined by how many kilometers of the full sections may be counted according to the rules set 
- Limited to top 2 options per station to reduce computational complexity
- Simple section-driven tracking (only counting unique section-traintype combinations)

## Known Limitations
- Limited to a 3-hour timeframe
- Only considers a small subset of stations
- Greedy approach may miss better solutions