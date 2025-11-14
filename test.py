import json
from pathlib import Path

INFO_PATH = Path(__file__).resolve().parent / 'information'


with open(INFO_PATH / 'station_codes.json', mode='r') as f:
    station_codes = json.load(f)
    
with open(INFO_PATH / 'station_distances.json', mode='r') as f:
    station_distances = json.load(f)
    
print('-'*50)
print("Processing station_codes..")
for code, name in station_codes.items():
    code_in_dict = False
    
    for dist_dict in station_distances:
        if code == dist_dict['fromStation'] or code == dist_dict['toStation']:
            code_in_dict = True
        
    if not code_in_dict:
        print(f"Station {name} with code `{code}` not found!")
        
print()
print('-'*50)
for dist_dict in station_distances:
    from_in_codes = False
    to_in_codes = False
    
    for code, _ in station_codes.items():
        if dist_dict['fromStation'] == code:
            from_in_codes = True
        elif dist_dict['toStation'] == code:
            to_in_codes = True
            
    if not from_in_codes:
        print(f"Code `{dist_dict['fromStation']}` not found!")
    if not to_in_codes:
        print(f"Code `{dist_dict['toStation']}` not found!")