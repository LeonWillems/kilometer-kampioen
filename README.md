# Kilometer Kampioen
Drive as many kilometers by train as possible within 24 hours - with the help of a computer

## Setup and Usage
1. Install requirements.txt
2. First, process the raw timetable data by running:
   ```bash
   python -m kilometer-kampioen.data_processing.process_timetable
   ```
   This will create the necessary processed timetable files in the `data` directory.

3. Run the route finding algorithm:
   ```bash
   python -m kilometer-kampioen.route_finding.greedy_dfs
   ```

   The main parameters in `greedy_dfs.py` that you can modify are:
   - `version`: Version of the timetable data (default: 'v0')
   - `end_time`: Time by which the route must be completed (default: 15:00)
   - `min_transfer_time`: Minimum transfer time in minutes (default: 3)
   - `max_transfer_time`: Maximum transfer time in minutes (default: 15)
   - `current_time`: Starting time (default: 12:00)
   - `current_station`: Starting station (default: 'Ht' - 's-Hertogenbosch)

   These parameters can be modified in the `main()` function of `greedy_dfs.py`.

### Output
The algorithm will create:
- Log files in `route_finding/logs/v0/` with detailed information about the search process
- Route files in `route_finding/routes/v0/` containing the best routes found, named with timestamp and distance in hectometers

# Sources
- Find all rules here: https://www.kilometerkampioen.nl/
- Find all station-related content here: https://en.wikipedia.org/wiki/Railway_stations_in_the_Netherlands
    - Each station has a code. For example, "Eindhoven Centraal" has "Ehv". Please find all codes in "stations/station_codes.csv"
- Find kilometer count courtesy here: https://github.com/nanderv/trainkms
    - A written guide how to count kilometers
    - A tool for counting kilometers
    - Number of kilometers between pairs of stations ("data/distance_between_stations.json")

# V0
## Data (see "data/mock_..." files)
- Intercity stations: 's-Hertogenbosch, Tilburg, Eindhoven Centraal
- Other stations: Vught, Boxtel, Best, Oisterwijk, Eindhoven Strijp-S
- Timeframe: Saturday, 12:00 - 15:00
- Actual train times for Saturday August 2nd, 2025

## Algorithm
- Implementation: Greedy Depth-First Search
- Scoring function: distance/(waiting_time + travel_time)
- Limited to top 2 options per station to reduce computational complexity
- Simple section-driven tracking (only counting unique section-traintype combinations)

## Known Limitations
- Does not fully implement Kilometer Kampioen rules
- Limited to a 3-hour timeframe
- Only considers a small subset of stations
- Greedy approach may miss better solutions
- Simplified transfer rules