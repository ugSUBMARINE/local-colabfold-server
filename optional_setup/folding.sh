#!/bin/bash/

time=$(date +%s)
dir_path="/mnt/ssd2/colabfold/${time}"
out_dir="${dir_path}/out"
mkdir $dir_path
mkdir $out_dir 
printf "+++ Use the following command to copy your fasta file from your computer to cfolding +++\n\n"
printf "scp /PATH/TO/MY/FASTA cfolding@143.50.46.7:${dir_path}\n\n"
printf "+++ To run a structure prediction enter the following command +++\n\n"
printf "jsb 'colabfold_batch ${dir_path}/MYFASTA.fasta ${out_dir}'\n\n"
printf "+++ To run a structure prediction without staying in your concole enter the following command +++\n\n"
printf "nohup jsb 'colabfold_batch ${dir_path}/MYFASTA.fasta ${out_dir}' > /mnt/ssd2/cf_nohup/${time}.out &\n\n"
printf "+++ Save the following command to get your data when it is finished +++\n\n"
printf "scp -r cfolding@143.50.46.7:${dir_path} /PATH/ON/YOUR/COMPUTER\n\n"

