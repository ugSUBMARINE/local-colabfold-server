#/bin/bash

path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"

server_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')
python_path=$(grep python_path "$path_path" | sed 's/.*://')
storage_path=$(grep storage_base "$path_path" | sed 's/.*://')

# base path of the saved scheduled jobs
base_path="${server_path}/schedule/"
exeshed_path="${base_path}execution_shedule.txt"

function remove_script() {
    # remove the script from the queue but check if queue got altered 
    ori_len=$(wc -l < $exeshed_path)
    tmpfile=$(mktemp "${base_path}/exeshed.XXXXXXX")
    tail -n +2 "$exeshed_path" > "$tmpfile"
    new_len=$(wc -l < $exeshed_path)
    if [ ! "$ori_len" -eq "$new_len" ];then
        # try again since the file length changed in the mean time
        echo "HOLD UP"
        rm "$tmpfile"
        sleep 0.5
        remove_script
    else
        echo "MOVING ${exeshed_path}"
        mv "$tmpfile" "$exeshed_path" 
    fi
        
}

if [ -e "$base_path" ]; then
    # get the first scheduled script path
    pre_file_name () { "$python_path" "${server_path}/get_script.py"; }
    file_name=$(pre_file_name)
    if [ ! "${file_name}" == "WAIT" ]; then 
        now=$(date +%Y-%m-%d-%H-%M-%S)
        # execute the script and log the execution
        if [ -f "$file_name" ];then
            echo "${now}    ${file_name}" > "${storage_path}/.shutdown/work.active"
            echo "**** ${now} EXECUTING ${file_name} ****"
            bash "$file_name" 
            ret_val=$?
            # remove the script from the schedule
            remove_script
            chmod +rw "$exeshed_path"
            chmod o+rw "$exeshed_path"
            echo "RETURNVALUE:${ret_val}~~${now}~~${file_name}" >> "${base_path}log.file"
            rm "${storage_path}/.shutdown/work.active"
        else
            echo "xxx FAILED accessing ${file_name} xxx"
            echo "FAILED ${now}~~${file_name}" >> "${base_path}log.file"
            remove_script
        fi
    fi
fi
