#!/bin/bash


path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"

storage_path=$(grep storage_base "$path_path" | sed 's/.*://')
server_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')

date +%Y-%m-%d-%H-%M-%S

for i in $(find "${storage_path}" -mindepth 1 -type d -mtime 7 -not -name ".shutdown" -and -not -name ".backup" | awk ' BEGIN { FS = "/" } length($6) > 1  { print $5"/"$6 }' | sort | uniq); do
    rm -r "$storage_path/${i}"
    rm "$storage_path/${i}.zip"
done
 find "${server_path}/schedule/exe_scripts/" -mindepth 1  -type f -mtime +7 -delete

if [ ! -d "$storage_path" ];then
    mkdir "$storage_path"
fi
