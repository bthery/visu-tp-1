#!/usr/bin/env python3

'''
Filters original data set to create the list of all stations
One entry per station: (station_id, station_lat, station_long)
Requires Python 3.6
'''

import csv
import sys

from collections import OrderedDict
from enum import Enum

def filter_stations(in_filename, out_filename):
    stations = {}
    incomplete_rows = 0

    # Read CSV and build unique list of stations
    with open(in_filename, 'r') as cvsfile:
        reader = csv.DictReader(cvsfile, delimiter=';')
        for row in reader:
            s_id = row['Starting Station ID']
            s_lat = row['Starting Station Latitude']
            s_long = row['Starting Station Longitude']
            if s_id == '' or \
               s_lat == '' or s_lat == '0' or \
               s_long == '' or s_long == '0':
                #print(f"Skip row: {s_id} ; {s_lat} ; {s_long}")
                incomplete_rows += 1
                continue
            if not s_id in stations:
                stations[s_id] = (s_lat, s_long)

    # Write CSV
    sorted_stations = OrderedDict(sorted(stations.items(), key=lambda t: t[0]))

    with open(out_filename, 'w', newline='') as csvfile:
        fieldnames = ['station_id', 'station_lat', 'station_long']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')

        writer.writeheader()
        for s_id in sorted_stations:
            s_lat = sorted_stations[s_id][0]
            s_long = sorted_stations[s_id][1]
            print(f"id:{s_id} lat:{s_lat} long:{s_long}")
            writer.writerow({'station_id': s_id, 'station_lat': s_lat, 'station_long': s_long})

    print('{} stations found'.format(len(sorted_stations)))
    print(f'{incomplete_rows} rows with incomplete data skipped')

if __name__ == "__main__":
    if (len(sys.argv) != 3):
        print(f"Usage: {sys.argv[0]} input_csv output_csv")
        sys.exit()
    filter_stations(sys.argv[1], sys.argv[2])

