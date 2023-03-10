# local-colabfold-server

This repository contains code to build a website on top of [localcolabfold](https://github.com/YoshitakaMo/localcolabfold) repository of [colabfold](https://github.com/sokrypton/ColabFold) that can be run on a local machine.
It is meant to provide an easy access to the core functions of colabfold.
The python version is based on the colabfold requirements **3.8.12**.
**It is tested on Ubuntu 22.04**

The account you install everything on should be a non admin account with the ability to use `sudo`.

***THIS IS MEANT TO RUN ON A LOCAL NETWORK***


## Things that can be set in the PARAMETERS section of the setup file
*   `add_cronjobs`
    *   whether to add cron jobs that remove files older than one week in the `storage_dir`
*   `mount_drives`
    *   check whether ssd needs to be mounted
*   `storage_dir`
    * specifies the directory (as absolute bath) in which the colabfold outputs should be stored
*   `check_openssh`
    * checks if openssh-server is installed


### In order to set things up just run the `bash setup_cfolding.sh` from within this repository. This will do the following things
*   checks if git, wget and openssh-server are installed
*   give instructions to mount the SSD as `ssd2` if one wants
*   create tokens in `./loc_production_server/tokens/`
*   create two directories in `storage_dir` to store colabfold results and nohub output of the colabfold runs and make them accessible to all user
*   adding cron jobs to remove files older than one week from these directories
*   cloning the bash job scheduler software and installing it in $HOME
*   installing Miniconda in $HOME
*   installing localcolabfold in $HOME/localcolabfold
*   giving instructions how to run everything as a server


### The website can be used in the following way
*   visiting the local IP adress through any browser
*   reading the guide
*   looking at the example fasta files
*   uploading a fasta file of the protein of interest with:
    *   a user name which creates a folder with the same name in /mnt/ssd2/colabfold where the results will be stored
    *   a token
        +   these are stored in tokens/registered_tokens.txt
*   downloading the results with the right user name from downloads
### Indentional restrictions
  +   one token can only queue **3 jobs** so the server can't get overfilled with requests
  +   the server accepts only **10 queued jobs** - after that new submissions will be blocked until less than 10 jobs are queued
      +   this can be changed in https://github.com/ugSUBMARINE/local-colabfold-server/blob/5192bd434d5a65b0bc89f782bb7ab3666ab4b87f/loc_production_server/pre_app.py#L89-L90  
  +   one fasta file can only contain a maximum of **3 sequence (header)**
      +   this can be changed with adding ` ,max_protein=N` at https://github.com/ugSUBMARINE/local-colabfold-server/blob/5192bd434d5a65b0bc89f782bb7ab3666ab4b87f/loc_production_server/pre_app.py#L201
