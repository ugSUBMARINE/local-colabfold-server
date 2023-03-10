# local-colabfold-server

This repository contains code to build a website on top of [localcolabfold](https://github.com/YoshitakaMo/localcolabfold) repository of [colabfold](https://github.com/sokrypton/ColabFold) that can be run on a local machine.
It is meant to provide an easy access to the core functions of colabfold.
The python version is based on the colabfold requirements **3.8.12**.
**It is tested on Ubuntu 22.04**

The whole program assumes to be installed on a user with the name `cfolding` which has an extra SSD to store all files. This should be a non admin account with the ability to use `sudo`.

***THIS IS MEANT TO RUN ON A LOCAL NETWORK***

In order to set things up just run the `bash setup_cfolding.sh` from within this repository. This will do the following things:
*   give instructions to mount the SSD as `ssd2` if not done
*   create tokens
*   create two directories in `/mnt/ssd2` to store colabfold results and nohub output of the colabfold runs and make them accessible to all user
    *   adding cron jobs to remove files older than one week from these directories
*   installing git if not present
*   cloning a bash scheduler software and installing it
*   installing openssh-server if not already installed
*   installing Miniconda
*   installing localcolabfold
*   giving instructions how to run everything as a server


The website can be used in the following way:
*   Visiting the local IP adress through any browser
*   Reading the guide
*   looking at the example fasta files
*   uploading a fasta file of the protein of interest with:
    *   a user name which creates a folder with the same name in /mnt/ssd2/colabfold where the results will be stored
    *   a token
        +   these are stored in tokens/registered_tokens.txt
        +   one token can only queue 3 jobs so the server can't get overfilled with requests
*   downloading the results with the right user name from downloads

