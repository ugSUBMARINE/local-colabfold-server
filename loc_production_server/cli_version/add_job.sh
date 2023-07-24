#!/bin/bash

path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"
storage_path=$(grep storage_base "$path_path" | sed 's/.*://')
colabfold_path=$(grep colabfold_path "$path_path" | sed 's/.*://')
python_path=$(grep python_path "$path_path" | sed 's/.*://')
loc_prod_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')

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

if [ ! -d "${storage_path}/${user}" ]; then
    mkdir "${storage_path}/${user}"
fi
project_dir="${storage_path}/${user}/${project_name}"
mkdir "$project_dir" 

mv "${file_name}" "$project_dir" 
ret_mv="$?"
if [ ! "$ret_mv" -eq "0" ]; then
    echo "Couldn't move fasta file to it's destination - check the file name"
    echo "Abandoning script"
    exit 1
fi

fasta_path="${project_dir}/${file_name}"
colabfold_command="${colabfold_path} ${fasta_path} ${project_dir}/out ${add_settings}"
zipping_command="${python_path} ${loc_prod_path}/zipping.py -f ${project_dir} -d ${project_dir}"
<<<<<<< Updated upstream
"${python_path}" cli_schedule.py -n "$project_name" -c "${colabfold_command},${zipping_command}"
=======
"${python_path}" ${loc_prod_path}/cli_version/cli_schedule.py -n "$project_name" -c "${colabfold_command},${zipping_command}"
>>>>>>> Stashed changes
