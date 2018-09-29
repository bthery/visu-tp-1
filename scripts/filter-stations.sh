#!/bin/bash

CSV_FILE=${1:-metro-bike-share-trip-data.csv}
OUT_CSV_FILE=${2:-stations.csv}

filter_starting_stations() {
    # Filter starting stations: build table containing one entry per station: (id;latitude;longitude)
    # Remove entries with missing data
    local out_file=$1
    echo "Station ID;Station Latitude;Station Longitude" > $out_file
    awk -F ';' '{ print $5";"$6";"$7 }' $CSV_FILE | sort | uniq | grep -v -E "^Starting|;;|0;0" >> $out_file
}

filter_ending_stations() {
    # Filter ending stations: build table containing one entry per station: (id;latitude;longitude)
    # Remove entries with missing data
    local out_file=$1
    echo "Station ID;Station Latitude;Station Longitude" > $out_file
    awk -F ';' '{ print $8";"$9";"$10 }' $CSV_FILE | sort |  uniq | grep -v -E "^Ending|;;|0;0" >> $out_file
}

filter_starting_stations $OUT_CSV_FILE 

# Just to make sure we have the same data than starting stations
#filter_ending_stations ending_stations.csv
#diff -Nurp starting_stations.csv ending_stations.csv
