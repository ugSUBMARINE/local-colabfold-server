#!/bin/bash

base_path="/mnt/ssd2/colabfold/"

user="$1"
path="$2"
file_name="$3"
add_settings="$4"

scp "${user}:${path}" . 
ret_scp="$?"
if [ ! "$ret_scp" -eq "0" ]; then
    echo "Couldn't scp fasta file"
    echo "Abandoning script"
    exit 1
fi

user="${user%%@*}"
time=$(date +%Y%m%d_%H%M%S)
project_name="${file_name%%.*}_$time"

if [ ! -d "${base_path}${user}" ]; then
    mkdir "${base_path}${user}"
fi
project_dir="${base_path}${user}/${project_name}"
mkdir "$project_dir" 

mv "${file_name}" "$project_dir" 
ret_mv="$?"
if [ ! "$ret_mv" -eq "0" ]; then
    echo "Couldn't move fasta file to it's destination - check the file name"
    echo "Abandoning script"
    exit 1
fi

fasta_path="${project_dir}/${file_name}"
colabfold_command="/home/cfolding/localcolabfold/colabfold-conda/bin/colabfold_batch ${fasta_path} ${project_dir}/out ${add_settings}"
zipping_command="/home/cfolding/localcolabfold/colabfold-conda/bin/python3 /home/cfolding/local-colabfold-server/loc_production_server/zipping.py -f ${project_dir} -d ${project_dir}"
python cli_schedule.py -n "$project_name" -c "${colabfold_command},${zipping_command}"
