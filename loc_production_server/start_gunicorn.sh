#!/bin/bash

path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"

gunicorn_path=$(grep gunicorn_path "$path_path" | sed 's/.*://')
server_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')
storage_path=$(grep storage_base "$path_path" | sed 's/.*://')

if [ ! -d "${storage_path}/.shutdown" ]; then
    mkdir "${storage_path}/.shutdown"
fi

"${gunicorn_path}" --reload --log-file "${server_path}/log_files/error.log" -w 4 -p "${server_path}/log_files/app.pid" --capture-output --chdir "$server_path" -D app:app
sleep 30
cp "${server_path}/log_files/app.pid" "${storage_path}/.shutdown/app.pid"
chmod o+rw "${storage_path}/.shutdown/app.pid"
