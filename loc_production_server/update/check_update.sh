#!/bin/bash

error_message(){
	echo "$1" && exit 1
}

test_paths(){
    if [ ! "${#1}" -gt 0 ];then
        echo "ERROR: Defined path $1 not readable" && exit 1
    fi
    if [ ! -e "$1" ];then
        echo "ERROR: Path '$1' does not exit" && exit 1
    fi
}

path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"
loc_prod_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')
python_path=$(grep python_path "$path_path" | sed 's/.*://')
git_path=$(grep git_path "$path_path" | sed 's/.*://')
docker_cmd=$(grep docker_path "$path_path" | sed 's/.*://')
storage_path=$(grep storage_base "$path_path" | sed 's/.*://')
weights_path=$(grep weights_path "$path_path" | sed 's/.*://')
db_path=$(grep db_path "$path_path" | sed 's/.*://')


a=("$path_path" "$loc_prod_path" "$python_path" "$git_path" "$docker_cmd" "$storage_path" "$weights_path" "$db_path")
for i in "${a[@]}";do
    test_paths "$i"
done

# threshold for deviation of new structure prediction to the reference
threshold=1.0

# remove unused docker container
echo '>>> removing unused docker container <<<'
"$docker_cmd" container prune -f

echo '>>> stashing changes, pulling new commits and applying stashed changes <<<'
cd "$git_path" || error_message "ERROR: Failed to change to repository directory"
pwd

# check for new commits
if [[ $(git rev-parse HEAD) = $( git ls-remote -q | grep "refs/heads/main" | cut -f1) ]];then
    exit 0
else
    date
fi

get the new commits and add stashed changes again
git stash || error_message "ERROR: Failed to stash changes"
git pull origin main || error_message "ERROR: Failed to pull in new changes"
git stash apply || error_message "ERROR: Failed to apply previous changes"

# create new docker image with new alphafold changes
echo '>>> creating new docker image <<<'
"$docker_cmd" build -t alphafold3_new -f docker/Dockerfile . || error_message "ERROR: Failed to build new image"

# make path to store newly predicted structure
echo '>>> making directory for new predicted reference structure <<<'
now=$(date +%d%m%y)
update_struct_path="$storage_path/update_${now}"
if [ ! -d "$update_struct_path" ];then
    mkdir "$update_struct_path" || error_message "ERROR: Failed to create new structure directory"
fi

# predict reference structure with new alphafold image
echo '>>> predicting new referencer structure <<<'
"$docker_cmd" run --volume "$loc_prod_path/update":/root/af_input --volume "$update_struct_path":/root/af_output --volume "$weights_path":/root/models --volume "$db_path":/root/public_databases --gpus all alphafold3_new python run_alphafold.py --json_path=/root/af_input/update.json --model_dir=/root/models --output_dir=/root/af_output 2>&1 | tee   "$update_struct_path/log.file" || error_message "ERROR: Failed to predict structure with newly created image"

# check the deviatin between the predictions
echo '>>> checking prediction deviation <<<'
prediction_deviation=$("$python_path" "$loc_prod_path/update/check_struct.py" -o "$loc_prod_path/update/reference.cif" -n $update_struct_path/*/*model.cif)
ret_val=$?
if [ "$ret_val" -gt 0 ];then
    echo "Failed to calculate the deviation between prediction and reference" && exit 1
fi

if (( $(echo "$prediction_deviation > $threshold" | bc -l) )); then
    echo "New prediction model deviates to much from old one" && exit 1
fi

if "$docker_cmd" image ls | grep -q alphafold3_bak;then
    "$docker_cmd" rmi alphafold3_bak || error_message "ERROR: Failed to remove backup image"
fi

echo '>>> creating docker backup image and renaming new image <<<'
"$docker_cmd" tag alphafold3 alphafold3_bak || error_message "ERROR: Failed to rename old image to backup image 'alphafold3_bak'"
"$docker_cmd" tag alphafold3_new alphafold3 || error_message "ERROR: Failed to rename new image to alphafold command name 'alphafold3'"
"$docker_cmd" rmi alphafold3_new || error_message "ERROR: Failed to rename new image backoff"
