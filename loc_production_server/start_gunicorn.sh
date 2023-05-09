#!/bin/bash

/home/cfolding/localcolabfold/colabfold-conda/bin/gunicorn --reload --log-file /home/cfolding/local-colabfold-server/loc_production_server/log_files/error.log -w 4 -p /home/cfolding/local-colabfold-server/loc_production_server/log_files/app.pid --capture-output --chdir /home/cfolding/local-colabfold-server/loc_production_server/ -D app:app
sleep 30
cp /home/cfolding/local-colabfold-server/loc_production_server/log_files/app.pid /mnt/ssd2/.shutdown/app.pid
chmod o+rw "/mnt/ssd2/.shutdown/app.pid"
