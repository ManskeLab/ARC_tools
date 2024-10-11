#! /bin/bash

XT2_HOST=$1
PULL_REQUEST=$2

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Prepare "pull to local" scripts
echo python $SCRIPT_DIR/check_xct.py $PULL_REQUEST $XT2_HOST ./
python $SCRIPT_DIR/check_xct.py $PULL_REQUEST $XT2_HOST ./

# Iterate through each file being pulled
rm log.txt
SKIP_FLAG=false
while IFS= read -r line
do
    id=${line%%echo*}
    command=${line##*echo}
    search_result=$(eval echo$command)
    if [[ "$search_result" = *"ISQ;"* ]]; then
        echo $id Exists! >> log.txt
    else
        echo $id Not Found >> log.txt
    fi
    # if line is tx push
done < sftp_check_log.txt