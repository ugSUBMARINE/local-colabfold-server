#/bin/bash

path_path="/home/cfolding/local-colabfold-server/directory_specification.txt"

server_path=$(grep loc_prod_path "$path_path" | sed 's/.*://')
python_path=$(grep python_path "$path_path" | sed 's/.*://')

sched_log_path="${server_path}/schedule/log.file"
stat_png_path="${server_path}/static/server_stats.png"


"${python_path}" "${server_path}/plot_stats.py" -i "${sched_log_path}" -o "${stat_png_path}"
