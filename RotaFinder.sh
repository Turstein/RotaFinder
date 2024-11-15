#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
trap 'echo "Error occurred in $0 at line $LINENO. Check $LOG_FILE for details."; exit 1' ERR

source ~/miniconda3/etc/profile.d/conda.sh
conda activate rotafinder

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Log file location
LOG_FILE="$SCRIPT_DIR/log.txt"

# Record start time
START_TIME=$(date +%s)
START_DATE=$(date +"%Y-%m-%d %H:%M:%S")
PWD=$(pwd)
echo "$START_DATE - Script started in $PWD" >> $LOG_FILE

# Loop through all directories in the current folder
for dir in */ ; do
  echo "Changing to directory: $dir"
  cd "$dir" || { echo "Failed to change to directory $dir"; exit 1; }
  folder_name=$(basename "$dir")
  
  # Run Trimmomatic
  trimmomatic PE *_R1_001.fastq.gz *_R2_001.fastq.gz \
    R1_paired.fastq.gz R1_unpaired.fastq.gz R2_paired.fastq.gz R2_unpaired.fastq.gz \
    ILLUMINACLIP:"$SCRIPT_DIR/adapters.fa":2:30:10:1 SLIDINGWINDOW:3:15 LEADING:3 TRAILING:3 MINLEN:36 || {
      echo "Trimmomatic failed in $folder_name"; exit 1; }

  # Run BBnorm
  bbnorm.sh in1=R1_paired.fastq.gz in2=R2_paired.fastq.gz out1=R1bbnorm.fastq.gz out2=R2bbnorm.fastq.gz target=100 min=5
  bbnorm.sh in1=R1_paired.fastq.gz in2=R2_paired.fastq.gz out1=R1bbnorm2.fastq.gz out2=R2bbnorm2.fastq.gz target=500 min=5

  # Run RNAviralSPAdes
  rnaviralspades.py -t 12 -1 R1bbnorm.fastq.gz -2 R2bbnorm.fastq.gz -o work1
  rnaviralspades.py -t 12 -1 R1bbnorm2.fastq.gz -2 R2bbnorm2.fastq.gz -o work2
  rnaviralspades.py -t 12 -1 R1_paired.fastq.gz -2 R2_paired.fastq.gz -o work3
  spades.py -t 12 --isolate --cov-cutoff auto -1 R1_paired.fastq.gz -2 R2_paired.fastq.gz -o work6

  # Run CollectFasta.py
  python3 "$SCRIPT_DIR/CollectFasta.py" || {
      echo "CollectFasta.py failed in $folder_name"; exit 1; }

  # Run Vigor4
  docker run -u $(id -u):$(id -g) -v "$(pwd)":/working_dir -w /working_dir -m 64g --cpus="8" \
    vigor4 bash -c "/home/vigor4/vigor4/bin/vigor4 -i contigs500.fasta -o vigor4 -d rtva" || {
      echo "Vigor4 failed in $folder_name"; exit 1; }

  # Run additional scripts
  bash "$SCRIPT_DIR/rotavarblast_sub.sh" || {
      echo "rotavarblast_sub.sh failed in $folder_name"; exit 1; }
  bash "$SCRIPT_DIR/rotablast.sh" || {
      echo "rotablast.sh failed in $folder_name"; exit 1; }

  cd ..
done

# Concatenate files
output_file="blast_rotavar.csv"
first_file=true

for dir in */; do
  file_path="${dir}blast_rota_genotyping.csv"
  if [[ -f "$file_path" ]]; then
    if $first_file; then
      cat "$file_path" > "$output_file"
      first_file=false
    else
      tail -n +2 "$file_path" >> "$output_file"
    fi
  fi
done

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED_TIME=$(($END_TIME - $START_TIME))

# Count folders processed
FOLDER_COUNT=$(find . -maxdepth 1 -type d | wc -l)
END_DATE=$(date +"%Y-%m-%d %H:%M:%S")

# Log the end of the script
echo "$END_DATE - Script ended in $PWD - Time spent: $ELAPSED_TIME seconds - Folders processed: $FOLDER_COUNT" >> $LOG_FILE
