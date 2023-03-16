# local-colabfold-server

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository contains code to build a website on top of the [localcolabfold](https://github.com/YoshitakaMo/localcolabfold) repository of [colabfold](https://github.com/sokrypton/ColabFold) that can be run on a local machine.
It is meant to provide an easy access to the core functions of colabfold.
The python version is based on the colabfold requirements **3.8.12**.
**It is tested on Ubuntu 22.04**

The account you install everything on should be a non admin account with the ability to use `sudo`.

***THIS IS MEANT TO RUN ON A LOCAL NETWORK***


## Things that can be set in the PARAMETERS section of the setup file
*   `add_cronjobs`
    *   Whether to add cron jobs that remove files older than one week in the `storage_dir`
*   `mount_drives`
    *   Check whether ssd needs to be mounted
*   `storage_dir`
    *   Specifies the directory (as absolute bath) in which the colabfold outputs should be stored
*   `pid_storage_dir`
    *   Specifies the directory where the `pid_storage` for the job scheduler is located - by default `/var/pid_storage/` is used.
*   `check_openssh`
    * Checks if openssh-server is installed


### In order to set things up just run the `bash setup_cfolding.sh` from within this repository. This will do the following things
*   Checks if git, wget and openssh-server are installed
*   Give instructions to mount the SSD as `ssd2` if one wants
*   Create tokens in `./loc_production_server/tokens/`
*   Create two directories in `storage_dir` to store colabfold results and nohub output of the colabfold runs and make them accessible to all user
*   Cloning the bash job scheduler software and installing it in $HOME
*   Installing Miniconda in $HOME
*   Installing localcolabfold in $HOME/localcolabfold
*   Adding cron jobs to remove files older than one week from these directories
*   Giving instructions how to run everything as a server


### The website can be used in the following way
*   Visiting the local IP adress through any browser
*   Reading the guide
*   Looking at the example fasta files
*   Uploading a fasta file of the protein of interest with:
    *   a user name which creates a folder with the same name in /mnt/ssd2/colabfold where the results will be stored
    *   a token
        +   these are stored in tokens/registered_tokens.txt
*   Downloading the results with the right user name from downloads
### Indentional restrictions
  +   One token can only queue **3 jobs** so the server can't get overfilled with requests
  +   The server accepts only **10 queued jobs** - after that new submissions will be blocked until less than 10 jobs are queued
      +   this can be changed in https://github.com/ugSUBMARINE/local-colabfold-server/blob/6752cbb9cc7b0f463e063f763d6b68956f139605/loc_production_server/pre_app.py#L32-L33
  +   One fasta file can only contain a maximum of **3 sequence (header)** and a maximum of **2500 amino acids**
      +   at https://github.com/ugSUBMARINE/local-colabfold-server/blob/6752cbb9cc7b0f463e063f763d6b68956f139605/loc_production_server/pre_app.py#L164
      +   the number of sequences can be changed with adding ` ,max_protein=N` 
      +   the number of amino acids can be changed with adding ` ,max_seqlen=L`


The images that are used as backgrounds were created using KerasCV's Stable Diffusion implementation.
