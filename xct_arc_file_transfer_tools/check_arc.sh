#! /bin/bash

PULL_REQUEST=$1

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Prepare "pull to local" scripts
echo python $SCRIPT_DIR/check_arc.py $PULL_REQUEST ./
python $SCRIPT_DIR/check_arc.py $PULL_REQUEST ./

# Iterate through each file being pulled
rm log_arc.txt
SKIP_FLAG=false
while IFS= read -r line
do
    id=${line%%xxx*}
    command=${line##*xxx}
    echo "$command"
    search_result=$(eval $command)
    echo ALERT:::: $search_result
    if [[ "$search_result" = "1" ]]; then
        echo $id Exists! >> log_arc.txt
    else
        echo $id Not Found >> log_arc.txt
    fi
    # if line is tx push
done < arc_check_log.txt