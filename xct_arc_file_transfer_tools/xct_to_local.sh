#! /bin/bash

ARC_HOST=arc
XT2_HOST=xt2
PULL_REQUEST=/Users/yousifalkhoury/work/images/sftp_pull_requests/pull_dynact.txt
ARC_TARGET_PATH=/work/manske_lab/images/hrpqct/dynact
FILE_CONVERTER=/Users/yousifalkhoury/scripts/Manskelab/scripts/fileConverter.py

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Prepare "pull to local" scripts
echo python $SCRIPT_DIR/get_xct.py $PULL_REQUEST $XT2_HOST ./ $ARC_HOST $ARC_TARGET_PATH
python $SCRIPT_DIR/get_xct.py $PULL_REQUEST $XT2_HOST ./ $ARC_HOST $ARC_TARGET_PATH

# scp -r ./temp/* $ARC_HOST:$ARC_TARGET_PATH

# Iterate through each file being pulled
SKIP_FLAG=false
while IFS= read -r line
do
    if [[ "$line" = "scp"* ]]
    then
        echo Skipping ARC transfer
        # # Push to ARC
        # if $SKIP_FLAG
        # then
        #     echo Skipping SCP transfer.
        # else
        #     echo Transferring image to ARC...
        #     eval $line
        # fi

    elif [[ "$line" = "sftp"* ]]
    then
        # Pull from XT2

        isq_image_dir=${line##* }
        nii_image_dir=${isq_image_dir%%.i*}.nii.gz
        nii_image_file=${nii_image_dir##*./temp/}

        echo Transferring image locally...

        eval $line
        echo

        # convert isq to nii.gz
        echo python $FILE_CONVERTER $isq_image_dir $nii_image_dir
        python $FILE_CONVERTER $isq_image_dir $nii_image_dir

        # remove isq
        echo Removing ISQ...
        rm $isq_image_dir
        echo
    fi

    # if line is tx push
done < sftp_fetch_log.txt