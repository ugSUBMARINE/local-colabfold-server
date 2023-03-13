#!/bin/bash 

################## START PARAMETERS ##################################
# TO CHANGE PARAMETERS 0 == YES and 1 == NO
add_cronjobs=0
mount_drives=0
storage_dir="/mnt/ssd2"
pid_storage_dir=""
check_openssh=0
################### END PARAMETERS ###################################

uname=$(whoami)
# check git and wget installation
type git || { echo "git not installed. Please install git first" ; exit 1 ; }
type wget || { echo "wget not installed. Please install wget first" ; exit 1 ; }
type nohup || { echo "nohup not installed. Please install wget first" ; exit 1 ; }

if [ "$check_openssh" -eq "0" ]; then
    # check installation of openssh-server for remote access
    if ! dpkg --list | grep "openssh-server" -q; then
        echo "Openssh-server not installed. Please install openssh-server first"
        echo ""
        exit 1
    fi
fi

# check mounting drives if necessary
if [ "$mount_drives" -eq "0" ]; then
    if ! cat /etc/fstab | grep "$storage_dir" -q; then
        echo "Mount ssd as ssd2"
        echo 'Get its UUID with sudo blkid'
        echo "Need to add them in /etc/fstab like:"
        echo "/dev/disk/by-uuid/THEIRUUID $storage_dir auto nosuid,nodev,nofail,x-gvfs-show 0 0"
        echo "After that restart the computer and rerun the script"
        exit 1
    fi
fi

path_end="${storage_dir: -1}"
if [ ! "$path_end" == "/" ];then
    storage_dir="${storage_dir}/"
fi

# changing storage directory in pre_app.py
sed "s+/mnt/ssd2/+${storage_dir}+" loc_production_server/pre_app.py > tempsedfile ; mv loc_production_server/pre_app.py loc_production_server/original_pre_app.py ; mv tempsedfile loc_production_server/pre_app.py

# creating tokens
cd loc_production_server
python3 tokengenerator.py

# creating needed directories
if [ ! -d "$storage_dir/colabfold" ]; then
    echo "Creating expected directories colabfold and cf_nohup in $storage_dir"
    mkdir -p "$storage_dir/colabfold"
    chmod +rwx "$storage_dir/colabfold"
fi
if [ ! -d "$storage_dir/cf_nohup" ]; then
    mkdir -p "$storage_dir/cf_nohup"
    chmod +rwx "$storage_dir/cf_nohup"
fi

if [ "$add_cronjobs" -eq "0" ]; then
    echo ""
    echo "Adding cron jobs to automatically remove files older than a week"
    echo "Assuming server app will be installed in /home/$uname/loc_production_server"
    if ! crontab -l | grep "0 2 \* \* \* /home/$uname/.folding/clean.sh" -q; then
        echo "Adding file cleaning"
        (crontab -l ; echo "0 2 * * * /home/$uname/.folding/clean.sh") | crontab -
    fi
    if ! crontab -l | grep "0 \* \* \* \* /home/$uname/loc_production_server/clean_iplog.py" -q; then
        echo "Adding iplog cleaning"
        (crontab -l ; echo "0 * * * * /home/$uname/loc_production_server/clean_iplog.py") | crontab -
    fi
fi

cd $HOME

# cloning job scheduler
git clone https://github.com/gwirn/job-scheduler-bash.git
g_ret=$?
if [ $g_ret -ne 0 ];then
    echo "Couldn't download scheduler script from its repository https://github.com/gwirn/job-scheduler-bash.git to $HOME- abandoning rest of the script"
    exit 1
fi
echo ""
echo "Setting up the scheduler"
cd job-scheduler-bash
chmod +x "$HOME/job-scheduler-bash/setup.sh"
bash -c "$HOME/job-scheduler-bash/setup.sh ${pid_storage_dir}"

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
mkdir -p localcolabfold
cd localcolabfold
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
echo "add --daemon flag if needed"
echo ""
