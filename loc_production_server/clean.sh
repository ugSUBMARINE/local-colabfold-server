#!/bin/bash


path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"

storage_path=$(grep storage_base "$path_path" | sed 's/.*://')
server_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')

find "${storage_path}/" -type f -mtime +7 ! -name ".shutdown" -exec rm -rf {} \;
find "${server_path}/schedule/exe_scripts/" -mindepth 1  -type f -mtime +7 -delete

if [ ! -d "$storage_path" ];then
    mkdir "$storage_path"
fi
