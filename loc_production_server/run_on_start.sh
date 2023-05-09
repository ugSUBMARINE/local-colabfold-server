#!/bin/bash

source /home/cfolding/.bashrc
startdate=$(date +%Y-%m-%d-%H-%M-%S)

echo "Started mashine ${startdate}" > "/mnt/ssd2/.shutdown/mashinestartup"

/bin/bash /home/cfolding/local-colabfold-server/loc_production_server/start_gunicorn.sh
ret="$?"

if [ "$ret" -eq "0" ]; then
    echo "${startdate} gunicorn start succeeded" >> "/mnt/ssd2/.shutdown/serverstartup"
    chmod o+rw "/mnt/ssd2/.shutdown/serverstartup"
else
    echo "${startdate} gunicorn start failed RETURNCODE: ${ret}" >> "/mnt/ssd2/.shutdown/serverstartup"
    chmod o+rw "/mnt/ssd2/.shutdown/serverstartup"
fi
