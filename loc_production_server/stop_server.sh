#/bin/bash

path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"

server_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')

kill $(cat "$server_path/log_files/app.pid")
