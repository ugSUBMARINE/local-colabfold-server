#!/bin/bash 

################## START PARAMETERS ##################################
# TO CHANGE PARAMETERS 0 == YES and 1 == NO
add_cronjobs=0
mount_drives=0
storage_dir="/mnt/ssd2"
pid_storage_dir="/var/pid_storage/"
check_openssh=0
################### END PARAMETERS ###################################

uname=$(whoami)
location="$(pwd)/"
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

base="${location}loc_production_server/"
# changing storage directory in pre_app.py
path_end="${storage_dir: -1}"
if [ ! "$path_end" == "/" ];then
    storage_dir="${storage_dir}/"
fi
tmpsed=$(mktemp ./tmpstore.XXXXXX)
sed "s+/mnt/ssd2/+${storage_dir}+" "${base}pre_app.py" > $tmpsed; mv "${base}pre_app.py" "${base}original_pre_app.py" ; mv $tmpsed "${base}pre_app.py"

# changing pid storage directory in pre_app.py
ppath_end="${pid_storage_dir: -1}"
if [ ! "$ppath_end" == "/" ];then
    pid_storage_dir="${pid_storage_dir}/"
fi
tmpsed=$(mktemp ./tmppid.XXXXXX)
sed "s+/var/pid_storage/+${pid_storage_dir}+" "${base}pre_app.py" > $tmpsed; rm "${base}pre_app.py" ; mv $tmpsed "${base}pre_app.py"

# changing colabfold directory in pre_app.py
tmpsed=$(mktemp ./tmpcolab.XXXXXX)
sed "s+/home/cfolding/colabfold_batch+${location}colabfold_batch+" "${base}pre_app.py" > $tmpsed; rm "${base}pre_app.py" ; mv $tmpsed "${base}pre_app.py"

# changing home directory in pre_app.py for sheduler
hpath="${HOME}/"
tmpsed=$(mktemp ./tmphome.XXXXXX)
sed "s+/home/cfolding/+${hpath}+" "${base}pre_app.py" > $tmpsed; rm "${base}pre_app.py" ; mv $tmpsed "${base}pre_app.py"

# creating tokens
cd "loc_production_server"
python3 tokengenerator.py
cd ..


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
    exec -l $SHELL
    echo ""
fi

exec -l $SHELL

echo "Downloading local colabfold installer script from its repository https://github.com/YoshitakaMo/localcolabfold to $HOME"

wget https://raw.githubusercontent.com/YoshitakaMo/localcolabfold/main/install_colabbatch_linux.sh
wg_ret=$?
if [ $wg_ret -ne 0 ];then
    echo "Couldn't download installer script - abandoning rest of the script"
    exit 1
fi

echo "Installing colabfold_batch"
bash install_colabbatch_linux.sh

if [ "$add_cronjobs" -eq "0" ]; then
    echo ""
    echo "Adding cron jobs to automatically remove files older than a week"
    if ! crontab -l | grep "0 2 \* \* \* /home/$uname/.folding/clean.sh" -q; then
        echo "Adding file cleaning"
        (crontab -l ; echo "0 2 * * * /home/$uname/.folding/clean.sh") | crontab -
    fi
    if ! crontab -l | grep "0 \* \* \* \* /home/$uname/loc_production_server/clean_iplog.py" -q; then
        echo "Adding iplog cleaning"
        (crontab -l ; echo "0 * * * * /home/$uname/loc_production_server/clean_iplog.py") | crontab -
    fi
fi

echo ""
echo "Install flask, gunicorn and eventlet in the conda environment of colabfold with pip"
echo "currently one needs to install gunicorn from so eventlet workers work"
echo "https://github.com/benoitc/gunicorn/archive/refs/heads/master.zip#egg=gunicorn==20.1.0"
echo ""
echo "Start the server from inside the loc_production_server directory with:"
echo "gunicorn --workers 12 -k eventlet -p log_files/app.pid app:app"
echo "add --daemon flag if needed"
echo ""
