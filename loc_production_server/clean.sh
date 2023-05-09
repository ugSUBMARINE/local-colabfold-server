#!/bin/bash
find /mnt/ssd2/cf_nohup/ -type f -mtime +7 -exec rm -r {} \;
find /mnt/ssd2/colabfold/ -type d -mtime +7 -exec rm -r {} \;
find /mnt/ssd2/colabfold/ -type f -mtime +7 -exec rm -r {} \;
find /home/cfolding/local-colabfold-server/loc_production_server/schedule/exe_scripts/ -type f -mtime +7 -exec rm -r {} \;
