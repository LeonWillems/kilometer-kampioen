# Kilometer Kampioen
Drive as many kilometers by train as possible within 24 hours - with the help of a computer

## Setup and Usage
1. Install requirements.txt
2. First, process the raw timetable data by running:
   ```bash
   python -m data_processing.process_timetable
   ```
   This will create the necessary processed timetable files in the `data` directory.

4. Fill in some parameters in the file below and run the route finding algorithm:
   ```bash
   python -m run
   ```

5. After running, can do some unit tests on the final route, to check if it's compliant with all the rules (work in progress). Will automatically grab the last route for given version.
   ```bash
   python -m tests.route_compliance
   ```

6. Visualize the found route:
   ```bash
   python -m visualization.plot_route
   ```

The main parameters in `settings.py` that you can modify are:
- `version`: Version of the timetable data (default: 'v1')
- `start_station`: Starting station (default: 'Ehv' - Eindhoven Centraal)
- `start_time`: Starting time (default: 08:00)
- `end_time`: Time by which the route must be completed (default: 20:00)
- `min_transfer_time`: Minimum transfer time in minutes (default: 3)
- `max_transfer_time`: Maximum transfer time in minutes (default: 15)


### Output
The algorithm will create:
- Log files in `runs/logs/v_/` with detailed information about the search process
- Parameters files in `runs/parameters/v_/` containing parameters filled in by user
- Route files in `runs/routes/v_/` containing the best routes found, named with timestamp and distance in hectometers
An example for each version can be found in `runs/example/v_/`

# Sources
## General
- Find all rules here: https://www.kilometerkampioen.nl/
- Find kilometer count courtesy here: https://github.com/nanderv/trainkms
   - Contains the 'ground-truth' kilometer distances used by kilometerkampioen
- Some detailed track information can be found here: https://spoorkaart.mwnn.nl/

## Data sources
- `data/`
   - `v0/mock_stations.png`: https://en.wikipedia.org/wiki/Railway_stations_in_the_Netherlands, edited with Paint
   - `v0/timetable_raw.csv`: Manually constructed with NS data from 2025-08-02
   - `v1/services-2025-10.csv`: Not included, need to download from https://www.rijdendetreinen.nl/en/open-data/train-archive
   - `v_/timetable.csv`: Obtained from preprocessing the raw dataset for some version
   - `v_/timetable_processed.csv`: Obtained from further processing of `timetable.csv`
   - `v_/intermediate_stations.json`: Contains all stations between any neighboring pair of hubs for some version
   - `station_distances_processed.json`: The processed version of `information/station_distances.json`
- `information/`
   - `kilometer_count_rules.png`: https://github.com/nanderv/trainkms/blob/main/rulesSuggestion.png
   - `rules.py`: https://www.kilometerkampioen.nl/handleiding
   - `scorecard.csv`: `scorekaart2023.xlsx`, but with the following changes: deleted both of the 'via HSL' lines, and adjusted some name to match `stations-2023-09.csv`. Cleaned up and kept the relevant information
   - `scorekaart2023.xlsx`: https://www.kilometerkampioen.nl/ -> 'Download Scorekaart'. Contains the kilometers between hub stations
   - `station_distances.json`: https://github.com/nanderv/trainkms/blob/main/routes.json -> With one minor change 'dtz' -> 'dtcp' (Delft Zuid -> Delft Campus)
   - `stations-2023-09.csv`: https://www.rijdendetreinen.nl/en/open-data/stations -> One minor change: ';' -> ',' for consistency among datasets
- `visualization/`
   - `spoorkaart-simple.png`: https://en.wikipedia.org/wiki/Railway_stations_in_the_Netherlands
   - `spoorkaart-extended.pdf`: https://www.treinreiziger.nl/spoorkaart-2019-deze-vier-versies-zijn-er/
   - `station_coordinates.json`: F*ckton of manual labor to get all coordinates

# V0
## Data (see `data/v0/` files)
- Intercity stations: 's-Hertogenbosch, Tilburg, Eindhoven Centraal
- Other stations: Vught, Boxtel, Best, Oisterwijk, Eindhoven Strijp-S
- Timeframe: Saturday, 12:00 - 15:00 (3 hours)
- Actual train times for Saturday August 2nd, 2025

## Algorithm
- Implementation: Greedy Depth-First Search
- Scoring function: counted_distance/(waiting_time + travel_time)
  - counted_distance is determined by how many kilometers of the full sections may be counted according to the rules set 
- Limited to top 2 options per station to reduce computational complexity
- Official section-driven calculation: see `information/rules.py`
For pseudocode, see `route_finding/pseudocode.py`.

## Known Limitations
- Limited to a 3-hour timeframe
- Only considers a small subset of stations
- Greedy approach may miss better solutions
- Due to DFS, it might take a while to find a better route

# V1
## Data (see `data/v1/` files)
- All Dutch rail stations
- Timeframe: Saturday: 08:00 - 20:00 (12 hours)
- Actual train times for Saturday October 4th, 2025

## Algorithm
- Same as for `V0`

## Known Limitations
- Train times dependent on one particular day, which contains disruptions
- Same DFS limitations as `V0`
