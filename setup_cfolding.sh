#!/bin/bash 

# mounting drives if necessary
if ! cat /etc/fstab | grep "/mnt/ssd2" -q; then
    echo "Mount ssd as ssd2"
    echo 'Get its UUID with sudo blkid'
    echo "Need to add them in /etc/fstab like:"
    echo "/dev/disk/by-uuid/THEIRUUID /mnt/ssd2 auto nosuid,nodev,nofail,x-gvfs-show 0 0"
    echo "After that restart the computer and rerun the script"
    # exit 1
fi

# creating tokens
cd loc_production_server
python3 tokengenerator.py

# creating needed directories
if [ ! -d "/mnt/ssd2/colabfold" ]; then
    echo "Creating expected directories colabfold and cf_nohup in /mnt/ssd2"
    mkdir "/mnt/ssd2/colabfold"
    chmod +rwx "/mnt/ssd2/colabfold"
fi
if [ ! -d "/mnt/ssd2/cf_nohup" ]; then
    mkdir "/mnt/ssd2/cf_nohup"
    chmod +rwx "/mnt/ssd2/cf_nohup"
fi

echo ""
echo "Adding cron jobs to automatically remove files older than a week"
echo "Assuming server app will be installed in /home/cfolding/loc_production_server"
if ! crontab -l | grep '0 2 \* \* \* /home/cfolding/.folding/clean.sh' -q;then
    echo "Adding file cleaning"
    (crontab -l ; echo "0 2 * * * /home/cfolding/.folding/clean.sh") | crontab -
fi
if ! crontab -l | grep '0 \* \* \* \* /home/cfolding/loc_production_server/clean_iplog.py' -q;then
    echo "Adding iplog cleaning"
    (crontab -l ; echo "0 * * * * /home/cfolding/loc_production_server/clean_iplog.py") | crontab -
fi

cd $HOME
if ! dpkg --list | grep ' git ' -q; then
    echo "Installing git with sudo apt install git"
    sudo apt install git
    echo ""
fi

# cloning job scheduler
git clone https://github.com/gwirn/job-scheduler-bash.git
g_ret=$?
if [ $g_ret -ne 0 ];then
    echo "Couldn't download scheduler script from its repository https://github.com/gwirn/job-scheduler-bash.git to $HOME- abandoning rest of the script"
    exit 1
fi
echo ""
echo "Setting up the scheduler"
bash "$HOME/job-scheduler-bash/setup.sh"

# installation of openssh-server for remote access
echo ""
if ! dpkg --list | grep "openssh-server" -q; then
    echo 'Running installation openssh-server with sudo apt install openssh-server'
    sudo apt install openssh-server
    echo ""
fi

# installation of miniconda
if ! conda --version >/dev/null; then
    echo "Downloading Miniconda3 installer"
    curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o Miniconda3-latest-Linux-x86_64.sh
    cu_ret=$?
    if [ cu_ret -ne 0 ]; then
        echo "Couldn't download Miniconda3 installer - abandoning rest of the script"
        exit 1
    fi
    echo "Installing miniconda"
    bash Miniconda3-latest-Linux-x86_64.sh
    b_ret=$?
    if [ cu_ret -ne 0 ]; then
        echo "Couldn't install Miniconda3 - abandoning rest of the script"
        exit 1
    fi
    echo ""
fi

echo "Downloading local colabfold installer script from its repository https://github.com/YoshitakaMo/localcolabfold to $HOME"
wget https://raw.githubusercontent.com/YoshitakaMo/localcolabfold/main/install_colabbatch_linux.sh
wg_ret=$?
if [ $wg_ret -ne 0 ];then
    echo "Couldn't download installer script - abandoning rest of the script"
    exit 1
fi

echo "Installing colabfold_batch"
bash install_colabbatch_linux.sh

if ! echo $PATH | grep "colabfold_batch" -q; then
    echo "Make sure colabfold is in the PATH and it is accessibel with colabfold_batch" 
fi

if ! dpkg --list | grep ' nginx ' -q; then
    echo "https://youtu.be/BpcK5jON6Cg" is a good instruction to set up nginx and gunicorn
fi

echo ""
echo "Install flask, gunicorn and eventlet in the conda environment of colabfold with pip"
echo "currently one needs to install gunicorn from so eventlet workers work"
echo "https://github.com/benoitc/gunicorn/archive/refs/heads/master.zip#egg=gunicorn==20.1.0"
echo ""
echo "Start the server from inside the server directory with:"
echo "gunicorn --workers 12 -k eventlet -p log_files/app.pid app:app"
echo ""
