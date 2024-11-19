#!/bin/bash

source ~/miniconda3/etc/profile.d/conda.sh
conda activate rotafinder

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LOG_FILE="$SCRIPT_DIR/log.txt"

START_TIME=$(date +%s)
START_DATE=$(date +"%Y-%m-%d %H:%M:%S")
PWD=$(pwd)
echo "$START_DATE - Script started in $PWD" >> $LOG_FILE

for dir in */ ; do
  cd "$dir" || continue
  folder_name=$(basename "$dir")

  echo "$START_DATE - Processing folder: $folder_name" >> $LOG_FILE 

  



  
  if ! bash "$SCRIPT_DIR/rotablast2.sh"; then
    echo "rotablast2.sh failed in $folder_name" >> $LOG_FILE
  fi

  cd ..
done

output_file="blast_rotavar3.csv"
first_file=true

for dir in */; do
  file_path="${dir}blast_rota_genotyping3.csv"
  if [[ -f "$file_path" ]]; then
    if $first_file; then
      cat "$file_path" > "$output_file"
      first_file=false
    else
      tail -n +2 "$file_path" >> "$output_file"
    fi
  fi
done

END_TIME=$(date +%s)
ELAPSED_TIME=$(($END_TIME - $START_TIME))
FOLDER_COUNT=$(find . -maxdepth 1 -type d | wc -l)
END_DATE=$(date +"%Y-%m-%d %H:%M:%S")

echo "$END_DATE - Script ended in $PWD - Time spent: $ELAPSED_TIME seconds - Folders processed: $(($FOLDER_COUNT - 1))" >> $LOG_FILE
