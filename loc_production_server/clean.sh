#!/bin/bash


path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"

storage_path=$(grep storage_base "$path_path" | sed 's/.*://')
server_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')

date +%Y-%m-%d-%H-%M-%S

# deletes results of run jobs
for i in $(find "${storage_path}" -mindepth 1 -type d -mtime 21 -not -name ".shutdown" -and -not -name ".backup" | awk ' BEGIN { FS = "/" } length($6) > 1  { print $5"/"$6 }' | sort | uniq); do
    rm -r "$storage_path/${i}"
    rm "$storage_path/${i}.zip"
done

# deletes the execution scripts for jobs 
find "${server_path}/schedule/exe_scripts/" -mindepth 1  -type f -mtime +21 -delete

# deletes user folders 
find "$storage_path" -mindepth 1 -type d -not -name ".shutdown" -not -name ".backup" -mtime +21 -exec rm -r {} \;

# deletes remaining update check files
for i in $(find "${storage_path}/update"*  ); do
    file=$(echo "$i" | grep -E '\/update_[0-9]{6}' | grep -v 'log.file')
    if [[ ! -z "$file" ]];then
        if [[ $(expr $(date +%d -r "$file") + 0) -gt 14 ]];then
            rm -r "$file"
        fi
    fi
done

if [ ! -d "$storage_path" ];then
    mkdir "$storage_path"
    mkdir "$storage_path/.shutdown"
    mkdir "$storage_path/.backup"
fi
