#!/bin/bash

path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"
docker_cmd=$(grep docker_path "$path_path" | sed 's/.*://')

docker_days_test=$("$docker_cmd" ps --format="{{.RunningFor}} {{.ID}}" | grep day | awk -F' ' '{if($1>=3) print$4}')
if [[ "$?" -eq 0 ]];then
    if [[ "$docker_days_test" ]];then
        for i in ${docker_days_test[@]};do
            date '+%d.%m.%Y %M:%H'
            docker stop "$i"
        done
    fi
else
    echo "Failed to get the running days of docker container"
fi
