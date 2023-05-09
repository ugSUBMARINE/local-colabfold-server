#/bin/bash

# base path of the saved scheduled jobs
base_path="/home/cfolding/local-colabfold-server/loc_production_server/schedule/"
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
    file_name=$(/home/cfolding/localcolabfold/colabfold-conda/bin/python3 /home/cfolding/local-colabfold-server/loc_production_server/get_script.py)
    if [ ! "${file_name}" == "WAIT" ]; then 
        now=$(date +%Y-%m-%d-%H-%M-%S)
        # execute the script and log the execution
        if [ -f "$file_name" ];then
            echo "${now}    ${file_name}" > /mnt/ssd2/.shutdown/work.active
            echo "**** ${now} EXECUTING ${file_name} ****"
            bash "$file_name" 
            ret_val=$?
            # remove the script from the schedule
            remove_script
            chmod +rw "$exeshed_path"
            chmod o+rw "$exeshed_path"
            echo "RETURNVALUE:${ret_val}~~${now}~~${file_name}" >> "${base_path}log.file"
            rm /mnt/ssd2/.shutdown/work.active
        else
            echo "xxx FAILED accessing ${file_name} xxx"
            echo "FAILED ${now}~~${file_name}" >> "${base_path}log.file"
            remove_script
        fi
    fi
fi
