#! /bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

ARC_HOST=arc
XT2_HOST=xt2
FILE_CONVERTER=$SCRIPT_DIR/fileConverter.py

PULL_REQUEST=$1
ARC_TARGET_PATH=$2

# Prepare "pull to local" scripts
echo python $SCRIPT_DIR/get_xct.py $PULL_REQUEST $XT2_HOST ./ $ARC_HOST $ARC_TARGET_PATH
python $SCRIPT_DIR/get_xct.py $PULL_REQUEST $XT2_HOST ./ $ARC_HOST $ARC_TARGET_PATH

ssh -qnx $ARC_HOST "mkdir $ARC_TARGET_PATH"
scp -r ./temp/* $ARC_HOST:$ARC_TARGET_PATH

# Iterate through each file being pulled
SKIP_FLAG=false
while IFS= read -r line
do
    if [[ "$line" = "scp"* ]]
    then
        # Push to ARC
        if $SKIP_FLAG
        then
            echo Skipping SCP transfer.
        else
            echo Transferring image to ARC...
            eval $line
        fi

    elif [[ "$line" = "sftp"* ]]
    then
        # Pull from XT2

        isq_image_dir=${line##* }
        nii_image_dir=${isq_image_dir%%.i*}.nii.gz
        nii_image_file=${nii_image_dir##*./temp/}

        echo Check if following file exists on arc...
        echo $nii_image_file
        echo 
        echo ssh -qnx $ARC_HOST "test -f $ARC_TARGET_PATH/$nii_image_file && echo 1 || echo 0"
        image_exists=$(ssh -qnx $ARC_HOST "test -f $ARC_TARGET_PATH/$nii_image_file && echo 1 || echo 0")
        echo

        if [[ "$image_exists" = "1" ]] 
        then
            echo Exists, skipping image.
            echo

            SKIP_FLAG=1
        else
            echo Does not exist, transferring image locally...

            eval $line
            echo

            # convert isq to nii.gz
            echo python $FILE_CONVERTER $isq_image_dir $nii_image_dir
            python $FILE_CONVERTER $isq_image_dir $nii_image_dir

            # remove isq
            echo Removing ISQ...
            rm $isq_image_dir
            echo

            SKIP_FLAG=0
        fi
    fi

    # if line is tx push
done < sftp_fetch_log.txt