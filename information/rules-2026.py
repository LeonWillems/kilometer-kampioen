"""

RULES FOR THE KILOMETER-KAMPIOEN COMPETITION

- 24-hour version: Start between 00:00 and 04:00
- 12-hour version: Start between 00:00 and 12:00
- In both cases: visit station Rotterdam Centraal between 11:00 and 15:00 for
    a stamp

Counting a connection:
- A connection is a direct route between two stations
- Every connection/traject can be counted:
  - Once before getting a stamp
  - Once after getting a stamp
- One exception on the rule:
  - Both before and after getting the stamp, one might count double:
    - Either Zwolle - Meppel
    - Or Sittard - Roermond

- As can be seen from the map, the HSL ('hoge snelheids lijn') has separate
    tracks it takes. More specifically, it rides its own route between
    Hoofddorp - Rotterdam Centraal, and between Rotterdam Lombardijen - Breda
    Prinsenbeek. Note that both Shl-Rtd and Bd-Rtd can only be counted once,
    as we are skipping the smaller stations.

- To make communication a bit easier, the Kilometer Kampioen organisation
    regards a 'traject' as a route from one intersection to the next
    - So, Vlissingen - Roosendaal is one 'traject' but consists of many
        intermediate stations

TODO: download and refer to right scorekaart
"""
