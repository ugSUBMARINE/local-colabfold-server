# local-colabfold-server

This repository contains code to build a web interface on top of the [localcolabfold](https://github.com/YoshitakaMo/localcolabfold) repository of [colabfold](https://github.com/sokrypton/ColabFold) as well as for [alphafold3](https://github.com/google-deepmind/alphafold3) that can be run on a local machine.
It is meant to provide an easy access to the core functions of colabfold as well as the full capability of alphafold 3.
The web interface is uncuppled from the structure prediction code.
The python version is based on the colabfold requirements **3.10.11**.


**It is tested on Ubuntu 22.04**

The account you install everything on should be a non admin account.

***THIS IS MEANT TO RUN ON A LOCAL NETWORK***


## Setup
*   Make sure to have git installed 
*   Make sure to have docker installed 
*   Download and install [localcolabfold](https://github.com/YoshitakaMo/localcolabfold)
*   Download [local-colabfold-sever](https://github.com/ugSUBMARINE/local-colabfold-server)
*   Download and install [alphafold3](https://github.com/google-deepmind/alphafold3)
*   Install the additionally required packages with `pip install -r requirements.txt`
*   Change the specified paths in `directory_specification.txt`
    *   `storage_base` : The base directory where all the results will be stored
    *   `colabfold_path` : The path to the coablfold bin
    *   `python_path` : The path to your python bin
    *   `gunicorn_path` : The path to your gunicorn bin
    *   `loc_prod_path` : The path to the `loc_production_server` directory of this repository
    *   `docker_path` : The path to the alphafold 3 docker container with an `alphafold3` image
    *   `weights_path` : The path to the alphafold 3 weights
    *   `db_path` : The path to the alphafold 3 data base
*   Add cronjobs with [crontab](https://www.man7.org/linux/man-pages/man1/crontab.1.html) to continuously check for jobs to execute
    * MINIMUM NEEDED CRONJOB
        * This checks every minute whether there is a job to run or not
        `* * * * * /bin/bash /home/cfolding/local-colabfold-server/loc_production_server/run.sh >> /home/cfolding/local-colabfold-server/loc_production_server/log_files/execution.log 2>&1`
    * RECOMMENDED cronjob setup instead of the MINIMUM
        * These will set checks for jobs to be executed 
        `* 7-20 * * 1-5 /bin/bash /home/cfolding/local-colabfold-server/loc_production_server/run.sh >> /home/cfolding/local-colabfold-server/loc_production_server/log_files/execution.log 2>&1`
        `30 20-23 * * 1-5 /bin/bash /home/cfolding/local-colabfold-server/loc_production_server/run.sh >> /home/cfolding/local-colabfold-server/loc_production_server/log_files/execution.log 2>&1`
        `59 0-7 * * 1-5 /bin/bash /home/cfolding/local-colabfold-server/loc_production_server/run.sh >> /home/cfolding/local-colabfold-server/loc_production_server/log_files/execution.log 2>&1`
        `30 * * * 6,0 /bin/bash /home/cfolding/local-colabfold-server/loc_production_server/run.sh >> /home/cfolding/local-colabfold-server/loc_production_server/log_files/execution.log 2>&1`
        * These start the web interface on server start and delete files to be only stored for 1 week
        `@reboot /bin/bash /home/cfolding/local-colabfold-server/loc_production_server/run_on_start.sh >> /mnt/ssd1/.shutdown/startup.log 2>&1`
        * `0 2 * * * /home/cfolding/local-colabfold-server/loc_production_server/clean.sh >> /home/cfolding/local-colabfold-server/loc_production_server/log_files/file_clean.log 2>&1`
        `0 * * * * /home/cfolding/localcolabfold/colabfold-conda/bin/python3 /home/cfolding/local-colabfold-server/loc_production_server/clean_iplog.py 2>&1`
        * restarts the the web interface upon crash
        `0,15,30,45 7-19 * * * if ! ps -p $(cat /home/cfolding/local-colabfold-server/loc_production_server/log_files/app.pid) > /dev/null;then /bin/bash /home/cfolding/local-colabfold-server/loc_production_server/run_on_start.sh >> /mnt/ssd1/.shutdown/startup.lo g; fi`
        * create a new usage plot
        `0 2 * * * /bin/bash /home/cfolding/local-colabfold-server/loc_production_server/plot.sh >> /home/cfolding/local-colabfold-server/loc_production_server/log_files/plot.log 2>&1`
        * backup all logfiles and the schedule
        `0 2 * * * /bin/bash /home/cfolding/local-colabfold-server/loc_production_server/backup.sh >> /home/cfolding/local-colabfold-server/loc_production_server/log_files/backup.log 2>&1`
*   These file paths need to be changed so the paths can be figured out - you will need to change the "/home/cfolding/" part of the links
    https://github.com/ugSUBMARINE/local-colabfold-server/blob/d4d1cbb634e9d080a956863403336fcce05cfe3f/loc_production_server/app_utils.py#L176
    https://github.com/ugSUBMARINE/local-colabfold-server/blob/d4d1cbb634e9d080a956863403336fcce05cfe3f/loc_production_server/clean.sh#L4
    https://github.com/ugSUBMARINE/local-colabfold-server/blob/d4d1cbb634e9d080a956863403336fcce05cfe3f/loc_production_server/cli_version/add_job.sh#L3
    https://github.com/ugSUBMARINE/local-colabfold-server/blob/d4d1cbb634e9d080a956863403336fcce05cfe3f/loc_production_server/run.sh#L3
    https://github.com/ugSUBMARINE/local-colabfold-server/blob/d4d1cbb634e9d080a956863403336fcce05cfe3f/loc_production_server/run_on_start.sh#L6
    https://github.com/ugSUBMARINE/local-colabfold-server/blob/d4d1cbb634e9d080a956863403336fcce05cfe3f/loc_production_server/start_gunicorn.sh#L3
    https://github.com/ugSUBMARINE/local-colabfold-server/blob/9b7058765478db9e64c423067a94abd4864e3001/loc_production_server/stop_server.sh#L3
*   Run `python loc_production_server/tokengenerator.py` to generate tokens
*   Run `bash loc_production_server/run_on_start.sh` to start the web interface
*   Run `bash loc_production_server/stop_server.sh` to stop the web interface

### The web interface can be used in the following way
*   Visiting the local IP address through any browser
*   Reading the guide
*   Looking at the example fasta files
*   Uploading a fasta file of the protein of interest with:
    *   a user name which creates a folder with the same name in `storage_base` where the results will be stored
    *   a token
        +   these are stored in `loc_prod_path/tokens/registered_tokens.txt`
    *   setting
        * number of model to generate
        * number of recycles
        * whether to use amber relax or not
*   Downloading the results with the right user name from downloads
    * This contains a zip file with all the results from colabfold except from the `envs` directory due to its size

### Intentional restrictions
  +   One token can only queue **3 jobs** so the server can't get overfilled with requests
  +   The server accepts only **10 queued jobs** - after that new submissions will be blocked until less than 10 jobs are queued
      +   this can be changed in https://github.com/ugSUBMARINE/local-colabfold-server/blob/6752cbb9cc7b0f463e063f763d6b68956f139605/loc_production_server/pre_app.py#L32-L33
  +   One json file can only contain a maximum of **3 sequence (header)** and a maximum of **3500 amino acids**
      +   at https://github.com/ugSUBMARINE/local-colabfold-server/blob/b8f8a55fefb4a13ae405c4aafa195f44535fa423/loc_production_server/pre_app.py#L201
      +   the number of sequences can be changed with adding ` ,max_protein=N` 
      +   the number of amino acids can be changed with adding ` ,max_seqlen=L`
  +   One fasta file can only contain a maximum of **3 sequence (header)** and a maximum of **2500 amino acids**
      +   at https://github.com/ugSUBMARINE/local-colabfold-server/blob/6752cbb9cc7b0f463e063f763d6b68956f139605/loc_production_server/pre_app.py#L164
      +   the number of sequences can be changed with adding ` ,max_protein=N` 
      +   the number of amino acids can be changed with adding ` ,max_seqlen=L`

### Created log files
There are several log files that get created to monitor what's happening (assuming the server gets started with `run_on_start.sh`)
*   on startup
    *   at `storage_path/.shutdown` :
        -   `machinestartup` : contains the date when the computer was started
        -   `serverstartup` : contains the date and whether the start of the web interface succeded or not
        -   `app.pid` : contains the PID of the master process of  gunicorn
    *   at `loc_prod_path/log_files` :
        -   `app.pid` : contains the PID of the master process of  gunicorn
        -   `error.log` : contains error and info about processes on the web interface
*   during production
    *   at `loc_prod_path/log_files` :
        -   `error.log` : contains error and info about processes on the web interface
        -   `execution.log` : contains all system output written by the running scripts/program/colabfold/...
        -   `ip.log` : contains which ip address visited which route
    *   at `loc_prod_path/schedule` :
        -   `log.file` : which driver bash script was executed when and what was the return value

### Create system files
Different system file will be created during the web interfaces activity to keep up with whats happening
*   at `loc_prod_path/tokens` 
    -   `registered_tokens.txt` : the registered tokens are stored there
*   at `storage_path/.shutdown`
    -   `work.active` : contains the name of the driver script as well as its start time and will be deleted after the script finished
*   at `loc_prod_path/schedule`
    -   `exe_scripts/SCRIPTNAME.sh` : the driver script for a colabfold run - it contains the colabfold command as well as the zip and token remove commands
    -   `execution_schedule.txt` : contains the paths to the driver scripts that need to be executed



The images that are used as backgrounds were created using KerasCV's Stable Diffusion implementation.
