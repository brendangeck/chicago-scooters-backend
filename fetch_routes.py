import csv
import googlemaps
from datetime import datetime
from os import path

gmaps = googlemaps.Client(key='AIzaSyCOgYCLxC8AoCZ-109UntNbLi58zfL52qo')

routes_file = 'routes.csv'
paths_file = 'scooter_paths.csv'

results = {}

def insert(lat0, lng0, lat1, lng1, encoded_points):
    lat0 = float(lat0)
    lng0 = float(lng0)
    lat1 = float(lat1)
    lng1 = float(lng1)

    if lat0 not in results.keys():
        results[lat0] = {}
    
    if lng0 not in results[lat0].keys():
        results[lat0][lng0] = {}
    
    if lat1 not in results[lat0][lng0].keys():
        results[lat0][lng0][lat1] = {}
    
    if lng1 not in results[lat0][lng0][lat1].keys():
        results[lat0][lng0][lat1][lng1] = None

    results[lat0][lng0][lat1][lng1] = encoded_points


def within(lat0, lng0, lat1, lng1):
    lat0 = float(lat0)
    lng0 = float(lng0)
    lat1 = float(lat1)
    lng1 = float(lng1)

    if lat0 not in results.keys():
        return False

    if lng0 not in results[lat0].keys():
        return False
    
    if lat1 not in results[lat0][lng0].keys():
        return False
    
    if lng1 not in results[lat0][lng0][lat1].keys():
        return False

    return True


def iter_items():
    for lat0 in results.keys():
        for lng0 in results[lat0].keys():
            for lat1 in results[lat0][lng0].keys():
                for lng1 in results[lat0][lng0][lat1].keys():
                    yield lat0, lng0, lat1, lng1, results[lat0][lng0][lat1][lng1]


# Fill results with any paths that have already been calculated
if path.exists(routes_file):
    with open(routes_file, 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader, None)  # skip the header

        for row in reader:
            encoded_points = row[4]
            insert(row[0], row[1], row[2], row[3], encoded_points)

# Call google maps service to provide any routes that have not been calculated yet
with open(paths_file, 'r', newline='') as f:
    reader = csv.reader(f)
    next(reader, None)  # skip the header

    row_num = 0
    count = 0
    for row in reader:
        print("READING ROW", row_num)

        if count > 5000:
            break

        if not within(row[5], row[6], row[7], row[8]):
            print("### FETCHING", row[5], row[6], row[7], row[8])

            directions_result = gmaps.directions(
                {'lat': row[5], 'lng': row[6]},
                {'lat': row[7], 'lng': row[8]},
                mode='bicycling',
                avoid=["highways", "tolls", "ferries"],
            )

            
            encoded_points = directions_result[0]['overview_polyline']['points']
            insert(row[5], row[6], row[7], row[8], encoded_points)
            count = count + 1
        row_num = row_num + 1

with open(routes_file, 'w', newline='') as f:
    csv_columns = ['origin_lat', 'origin_lng', 'dest_lat', 'dest_lng', 'encoded_points']
    writer = csv.DictWriter(f, fieldnames=csv_columns)
    writer.writeheader()
    for lat0, lng0, lat1, lng1, encoded_points in iter_items():
        row = {
            'origin_lat': lat0,
            'origin_lng': lng0,
            'dest_lat': lat1,
            'dest_lng': lng1,
            'encoded_points': encoded_points
        }

        writer.writerow(row)

