#!/bin/bash


head -n 1 ../ex02/hh_sorted.csv > hh_positions.csv

while IFS= read -r line; do
    IFS=',' read -r id created_at name has_test alternate_url <<< "$line"
    pos='-'
    p=$(echo $name | grep -Eo 'Senior|Middle|Junior' | tr '\n' '/')
    if [[ -n $p ]]; then
        pos=${p%/}
    fi
    echo "$id","$created_at","$pos","$has_test","$alternate_url" >> hh_positions.csv
done < ../ex02/hh_sorted.csv


