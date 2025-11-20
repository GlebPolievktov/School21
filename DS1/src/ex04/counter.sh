#!/bin/bash


echo "\"name\"","\"count\"" > hh_uniq_positions.csv


c_j=0
c_m=0
c_s=0
skip=0

while IFS= read -r line; do
    IFS=',' read -r id created_at name has_test alternate_url <<< "$line"
    
    if [[ "$name" == "Junior" ]]; then
        ((c_j++))
    elif [[ "$name" == "Senior" ]]; then
        ((c_s++))
    elif [[ "$name" == "Middle" ]]; then
        ((c_m++))
    elif [[ "$name" == "-" ]]; then
        ((skip++))
    fi
done < ../ex03/hh_positions.csv

echo ""Junior","$c_j"" >> hh_uniq_positions.csv
echo ""Middle","$c_m"" >> hh_uniq_positions.csv
echo ""Senior","$c_s"" >> hh_uniq_positions.csv
echo ""No_info","$skip"" >> hh_uniq_positions.csv