#!/usr/bin/env python3

'''
Filters original data set to aggregate the trips data

Produces one .csv files:
- (time_slot , time_slot_label, mean_weekday_trips, mean_weekend_trips)

Columns:
- time_slot: Day divided in 30 minutes time slot (24 * 2 = 48 slots/day)
- time_slot_label : Label for the start time of the slot (eg. 13:30)
- mean_weekday_trips : Mean number of trips started in this time slot per week days
- mean_weekend_trips : Mean number of trips started in this time slot per weekend days


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


def slot_to_time(slot):
    '''Convert slot index to a string representing the slot start time (eg. 13:30)'''
    hours = slot // slots_per_hours
    minutes = (slot % slots_per_hours) * slot_duration
    return f"{hours:02}:{minutes:02}"


def date_to_slot(date):
    '''Convert datetime object into a slot index'''
    return (date.hour * slots_per_hours) + (date.minute // slot_duration)


def insert_trip(date, weekday, weekend):
    '''Insert trip started a specified date into the relevant array depending on the day of the week'''
    is_weekend = (date.isoweekday() in (6, 7))
    slot = date_to_slot(date)
    if is_weekend:
        weekend[slot] += 1
    else:
        weekday[slot] += 1


def save_csv(weekday, weekend, out_filename):
    '''Export filtered data to .csv file'''
    slots_labels = [ slot_to_time(s) for s in range(slots_per_day)]

    with open(out_filename, 'w', newline='') as csvfile:
        fieldnames = ['time_slot', 'time_slot_label', 'mean_weekday_trips', 'mean_weekend_trips']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')

        writer.writeheader()
        for s in range(slots_per_day):
            print(f'slot:{s} label:"{slots_labels[s]}" weekday:{round(weekday[s])} weekend:{round(weekend[s])}')
            writer.writerow({'time_slot': s, \
                             'time_slot_label': slots_labels[s], \
                             'mean_weekday_trips': f'{weekday[s]:.2f}', \
                             'mean_weekend_trips': f'{weekend[s]:.2f}'})
    print(f"Data saved to {out_filename}")


def filter_trips(in_filename, out_directory):
    '''Read input .csv file and extract mean number of trips per time slots'''
    weekday_start = [0 for i in range(slots_per_day)]
    weekday_end   = [0 for i in range(slots_per_day)]
    weekend_start = [0 for i in range(slots_per_day)]
    weekend_end   = [0 for i in range(slots_per_day)]
    incomplete_rows = 0
    first = True

    # Read CSV and build unique list of stations
    with open(in_filename, 'r') as cvsfile:
        reader = csv.DictReader(cvsfile, delimiter=';')
        for row in reader:
            t_start = row['Start Time']
            t_end = row['End Time']
            if t_start == '' or t_end == '' :
                #print(f"Skip row: {trip} ; {t_start} ; {t_end}")
                incomplete_rows += 1
                continue
            # Convert time from "2017-03-19T14:18:00" format
            d_start = datetime.strptime(t_start, "%Y-%m-%dT%H:%M:%S")
            d_end = datetime.strptime(t_end, "%Y-%m-%dT%H:%M:%S")

            # Increment relevant slots
            insert_trip(d_start, weekday_start, weekend_start)
            insert_trip(d_end, weekday_end, weekend_end)

            # Get oldest and newest date
            if first:
                first = False
                min_date = d_start
                max_date = d_end
            else:
                min_date = min(min_date, d_start)
                max_date = max(max_date, d_end)

    # Divide counters in each slot by the number of relevant days
    delta_date = max_date - min_date
    weekday_start =  [ s / (delta_date.days * 5 / 7) for s in weekday_start]
    weekday_end   =  [ s / (delta_date.days * 5 / 7) for s in weekday_end]
    weekend_start =  [ s / (delta_date.days * 2 / 7) for s in weekend_start]
    weekend_end   =  [ s / (delta_date.days * 2 / 7) for s in weekend_end]

    # Display
    for a in (weekday_start, weekday_end, weekend_start, weekend_end):
        for s in a:
            print(f"{round(s)} / ", end='')
        print("\n")
    print(f"Mean starts/week day    = {round(sum(weekday_start))}")
    print(f"Mean ends/week days     = {round(sum(weekday_end))}")
    print(f"Mean starts/weekend day = {round(sum(weekend_start))}")
    print(f"Mean ends/weekend days  = {round(sum(weekend_end))}")

    print(f"Oldest date = {min_date}")
    print(f"Newest date = {max_date}")
    print(f"Days        = {delta_date.days}")
    print(f'{incomplete_rows} rows with incomplete data skipped')

    # Write CSV
    save_csv(weekday_start, weekend_start, os.path.join(out_directory, "mean_trips_per_day_per_time_slots.csv"))


if __name__ == "__main__":
    if (len(sys.argv) != 3):
        print(f"Usage: {sys.argv[0]} input_csv output_directory")
        sys.exit()
    filter_trips(sys.argv[1], sys.argv[2])

