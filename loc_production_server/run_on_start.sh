#!/bin/bash

source /home/cfolding/.bashrc
startdate=$(date +%Y-%m-%d-%H-%M-%S)

path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"
server_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')
storage_path=$(grep storage_base "$path_path" | sed 's/.*://')
base_storage_path=$(echo "${storage_path%/*}")

echo "Started mashine ${startdate}" > "${base_storage_path}/.shutdown/mashinestartup"

bash "${server_path}/start_gunicorn.sh" 
ret="$?"

if [ "$ret" -eq "0" ]; then
    echo "${startdate} gunicorn start succeeded" >> "${base_storage_path}/.shutdown/serverstartup"
    chmod o+rw "${base_storage_path}/.shutdown/serverstartup"
else
    echo "${startdate} gunicorn start failed RETURNCODE: ${ret}" >> "${base_storage_path}/.shutdown/serverstartup"
    chmod o+rw "${base_storage_path}/.shutdown/serverstartup"
fi
