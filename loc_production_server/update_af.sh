#!/bin/bash

path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"
loc_prod_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')
schedule_path="$loc_prod_path/schedule/execution_shedule.txt"

if [ "$(wc -l < $schedule_path)" -gt 0 ];then
    echo "Server is busy - retry in 2 h"
    sleep 7200
    if [ "$(wc -l < $schedule_path)" -gt 0 ];then
        echo "Server still busy - try next week" && exit 1
    fi
fi

echo "BLOCKING" > "$schedule_path"

ls "$loc_prod_path/update/check_update.sh"

tail -n+2  "$schedule_path" > "$schedule_path.tmp" 
mv "$schedule_path.tmp" "$schedule_path" 
