#!/usr/bin/env python3

'''
Trips per station per time slot

Filters original data set to aggregate the trips data

Produces two .csv files:
- One for the week days
- One for the weekend days

Columns: (station_id , start_slot_1, ..., start_slot_n, end_slot_1, ..., end_slot_n)

- station_id   : ID of the station
- start_slot_n : Number of trip that started in this station during this time slot
- end_slot_n   : Number of trip that ended in this station during this time slot

Day is divided in 30 minutes time slots (24 * 2 = 48 slots/day)

Usage:  ./aggregate-trips.py ../data/metro-bike-share-trip-data-xlsx.csv ../data/

Requires Python 3.6
'''

import csv
import os
import sys

from collections import OrderedDict
from datetime import datetime, timezone

# 30 minutes time slots
slot_duration   = 30
slots_per_hours = 60 // slot_duration
slots_per_day   = 24 * slots_per_hours

# Compute the mean number of trip per day
# (divide total number of trips by number of days in set)
mean_per_day = False

#
# { 'start': [ ], 'end': [ ] }
#
stations_weekend = {}
stations_weekday = {}
weekend_csv = "trips_per_station_per_time_slot_weekday.csv"
weekday_csv = "trips_per_station_per_time_slot_weekend.csv"

def slot_to_time(slot):
    '''Convert slot index to a string representing the slot start time (eg. 13:30)'''
    hours = slot // slots_per_hours
    minutes = (slot % slots_per_hours) * slot_duration
    return f"{hours:02}:{minutes:02}"


def date_to_slot(date):
    '''Convert datetime object into a slot index'''
    return (date.hour * slots_per_hours) + (date.minute // slot_duration)


def insert_station(station_id, station_lat, station_long):
    '''Insert new station in global stations dictionary and init slots values to 0'''
    for stations in (stations_weekday, stations_weekend):
        if not station_id in stations:
            stations[station_id] = {}
            stations[station_id]['lat']   = station_lat
            stations[station_id]['long']  = station_long
            stations[station_id]['start'] = [ 0 for i in range(slots_per_day)]
            stations[station_id]['end']   = [ 0 for i in range(slots_per_day)]
        else:
            # Try to fill missing data (there is a bunch of invalid rows in the data set)
            if stations[station_id]['lat'] in (0, ""):
                stations[station_id]['lat'] = station_lat
            if stations[station_id]['long'] in (0, ""):
                stations[station_id]['long'] = station_long


def insert_trip(start_station, start_date, end_station, end_date):
    '''Insert trip started at specified date into the relevant array depending on the day of the week'''

    # Increase relevant slot counter
    is_weekend = (start_date.isoweekday() in (6, 7))
    slot = date_to_slot(start_date)
    if is_weekend:
        stations_weekend[start_station]['start'][slot] += 1
    else:
        stations_weekday[start_station]['start'][slot] += 1

    is_weekend = (end_date.isoweekday() in (6, 7))
    slot = date_to_slot(end_date)
    if is_weekend:
        stations_weekend[end_station]['end'][slot] += 1
    else:
        stations_weekday[end_station]['end'][slot] += 1


def save_csv(stations, out_filename):
    '''Export filtered data to .csv file'''
    start_slots = [ f"start_slot_{slot}" for slot in range(slots_per_day)]
    end_slots   = [ f"end_slot_{slot}" for slot in range(slots_per_day)]

    with open(out_filename, 'w', newline='') as csvfile:
        fieldnames = ['station_id', 'station_lat', 'station_long'] + start_slots + end_slots
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')

        writer.writeheader()
        for station in stations:
            if stations[station]['lat'] == '' or \
               stations[station]['long'] == '' or \
               station in ("3009", "3039"):
                # Skip station with no coordinates or stations that in
                # the black list (too far from the other stations)
                continue

            row_dict = {
                'station_id' : station,
                'station_lat' : stations[station]['lat'],
                'station_long' : stations[station]['long']
            }
            for slot in range(slots_per_day):
                row_dict[f"start_slot_{slot}"] = stations[station]['start'][slot]
                row_dict[f"end_slot_{slot}"] = stations[station]['end'][slot]
            writer.writerow(row_dict)
    print(f"Data saved to {out_filename}")


def filter_trips(in_filename, out_directory):
    '''Read input .csv file and extract mean number of trips per time slots'''
    incomplete_rows = 0
    first = True

    # Read CSV and build unique list of stations
    with open(in_filename, 'r') as cvsfile:
        reader = csv.DictReader(cvsfile, delimiter=';')
        for row in reader:
            start_id   = row['Starting Station ID']
            start_lat  = row['Starting Station Latitude']
            start_long = row['Starting Station Longitude']
            start_time = row['Start Time']
            end_id     = row['Ending Station ID']
            end_lat    = row['Ending Station Latitude']
            end_long   = row['Ending Station Longitude']
            end_time   = row['End Time']

            # Is it a valid row?
            if start_time == '' or end_time == '' or \
               start_id == '' or end_id == '':
                incomplete_rows += 1
                continue

            # Convert time from "2017-03-19T14:18:00" format
            start_date = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
            end_date = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")

            # Insert station in dictionaries if it hasn't been seen before
            insert_station(start_id, start_lat, start_long)
            insert_station(end_id, end_lat, end_long)

            # Increment relevant slots
            insert_trip(start_id, start_date, end_id, end_date)

            # Get oldest and newest date
            if first:
                first = False
                min_date = start_date
                max_date = end_date
            else:
                min_date = min(min_date, start_date)
                max_date = max(max_date, end_date)

    # Divide counters in each slot by the number of relevant days
    delta_date = max_date - min_date
    if mean_per_day:
        for stations in (stations_weekday, stations_weekend):
            if stations is stations_weekday:
                days = (delta_date.days * 5 / 7)
            else:
                days = (delta_date.days * 2 / 7)
            for s in stations:
                stations[s]['start'] = [ count / days for count in stations[s]['start'] ]
                stations[s]['end']   = [ count / days for count in stations[s]['end'] ]

    # Display
    for stations in (stations_weekday, stations_weekend):
        for s in stations:
            print(f"Station:{s} ({stations[s]['lat']}, {stations[s]['long']})")
            print('Trip starts: ', end='')
            for count in stations[s]['start']:
                print(f"{count} / ", end='')
            print('\nTrip ends: ', end='')
            for count in stations[s]['end']:
                print(f"{count} / ", end='')
            print('\n')

    # print(f"Mean starts/week day    = {round(sum(weekday_start))}")
    # print(f"Mean ends/week days     = {round(sum(weekday_end))}")
    # print(f"Mean starts/weekend day = {round(sum(weekenstart_date))}")
    # print(f"Mean ends/weekend days  = {round(sum(weekenend_date))}")

    print(f"Oldest date = {min_date}")
    print(f"Newest date = {max_date}")
    print(f"Days        = {delta_date.days}")
    print(f'{incomplete_rows} rows with incomplete data skipped')
    total_trip_starts = 0
    total_trip_ends = 0
    for stations in (stations_weekday, stations_weekend):
        for s in stations:
            total_trip_starts += sum(stations[s]['start'])
            total_trip_ends += sum(stations[s]['end'])
    print(f'Total number of trips filtered: {total_trip_starts} / {total_trip_ends}')

    # Write CSV
    save_csv(stations_weekday, os.path.join(out_directory, weekday_csv))
    save_csv(stations_weekend, os.path.join(out_directory, weekend_csv))


if __name__ == "__main__":
    if (len(sys.argv) != 3):
        print(f"Usage: {sys.argv[0]} input_csv output_directory")
        sys.exit()
    filter_trips(sys.argv[1], sys.argv[2])

