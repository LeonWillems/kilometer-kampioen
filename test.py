sprinter_pairs = [
    "Fwd",
    "Hdg",
    "Lwc",
    "Lw"
]

for station_tuple in zip(
    sprinter_pairs[:-1], sprinter_pairs[1:]
):
    print(station_tuple)
    print(station_tuple[::-1])
    print(type(station_tuple))
    print('---------------')
