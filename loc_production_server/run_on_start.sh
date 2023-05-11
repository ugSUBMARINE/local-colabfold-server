#!/bin/bash

source /home/cfolding/.bashrc
startdate=$(date +%Y-%m-%d-%H-%M-%S)

path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"
server_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')
storage_path=$(grep storage_base "$path_path" | sed 's/.*://')

if [ ! -d "${storage_path}/.shutdown" ]; then
    mkdir "${storage_path}/.shutdown"
fi

echo "Started machine ${startdate}" > "${storage_path}/.shutdown/machinestartup"

bash "${server_path}/start_gunicorn.sh" 
ret="$?"

if [ "$ret" -eq "0" ]; then
    echo "${startdate} gunicorn start succeeded" >> "${storage_path}/.shutdown/serverstartup"
    chmod o+rw "${storage_path}/.shutdown/serverstartup"
else
    echo "${startdate} gunicorn start failed RETURNCODE: ${ret}" >> "${storage_path}/.shutdown/serverstartup"
    chmod o+rw "${storage_path}/.shutdown/serverstartup"
fi
