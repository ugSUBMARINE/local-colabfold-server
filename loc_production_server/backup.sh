#/bin/bash

path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"

server_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')
storage_path=$(grep storage_base "$path_path" | sed 's/.*://')

if [ ! -d "${storage_path}/.backup" ];then
    mkdir "${storage_path}/.backup"
fi

cp "${server_path}/log_files/"* "${storage_path}/.backup"
cp "${server_path}/schedule/log.file" "${storage_path}/.backup/schedule_log.file"
cp "${server_path}/schedule/execution_shedule.txt" "${storage_path}/.backup/execution_shedule.txt"
