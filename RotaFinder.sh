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

  # Run Trimmomatic
  if ! trimmomatic PE *_R1_001.fastq.gz *_R2_001.fastq.gz R1_paired.fastq.gz R1_unpaired.fastq.gz R2_paired.fastq.gz R2_unpaired.fastq.gz ILLUMINACLIP:"$SCRIPT_DIR/adapters.fa":2:30:10:1 SLIDINGWINDOW:3:15 LEADING:3 TRAILING:3 MINLEN:36; then
    echo "Trimmomatic failed in $folder_name, skipping folder." >> $LOG_FILE
    cd ..
    continue
  fi

  # Check if Trimmomatic output files are empty
  if [[ ! -s R1_paired.fastq.gz || ! -s R2_paired.fastq.gz ]]; then
    echo "Trimmomatic output files are empty in $folder_name, skipping folder." >> $LOG_FILE
    cd ..
    continue
  fi

  # Run BBnorm (target 100)
  if ! bbnorm.sh in1=R1_paired.fastq.gz in2=R2_paired.fastq.gz out1=R1bbnorm.fastq.gz out2=R2bbnorm.fastq.gz target=100 min=5; then
    echo "BBnorm (target=100) failed in $folder_name, skipping folder." >> $LOG_FILE
    cd ..
    continue
  fi

  # Check if BBnorm output files are empty
  if [[ ! -s R1bbnorm.fastq.gz || ! -s R2bbnorm.fastq.gz ]]; then
    echo "BBnorm (target=100) output files are empty in $folder_name, skipping running rnaviralspades.py work1." >> $LOG_FILE
  else
    # Run RNAviralSPAdes (Work1)
    if ! rnaviralspades.py -t 12 -1 R1bbnorm.fastq.gz -2 R2bbnorm.fastq.gz -o work1; then
      echo "rnaviralspades.py (work1) failed in $folder_name" >> $LOG_FILE
    fi
  fi

  # Run BBnorm (target 500)
  if ! bbnorm.sh in1=R1_paired.fastq.gz in2=R2_paired.fastq.gz out1=R1bbnorm2.fastq.gz out2=R2bbnorm2.fastq.gz target=500 min=5; then
    echo "BBnorm (target=500) failed in $folder_name, skipping folder." >> $LOG_FILE
    cd ..
    continue
  fi

  # Check if BBnorm output files are empty
  if [[ ! -s R1bbnorm2.fastq.gz || ! -s R2bbnorm2.fastq.gz ]]; then
    echo "BBnorm (target=500) output files are empty in $folder_name, skipping running rnaviralspades.py work2." >> $LOG_FILE
  else
    # Run RNAviralSPAdes (Work2)
    if ! rnaviralspades.py -t 12 -1 R1bbnorm2.fastq.gz -2 R2bbnorm2.fastq.gz -o work2; then
      echo "rnaviralspades.py (work2) failed in $folder_name" >> $LOG_FILE
    fi
  fi

  # Check if paired files from Trimmomatic are empty before running remaining analysis
  if [[ -s R1_paired.fastq.gz && -s R2_paired.fastq.gz ]]; then
    if ! rnaviralspades.py -t 12 -1 R1_paired.fastq.gz -2 R2_paired.fastq.gz -o work3; then
      echo "rnaviralspades.py (work3) failed in $folder_name" >> $LOG_FILE
    fi
    
    if ! spades.py -t 12 --isolate --cov-cutoff auto -1 R1_paired.fastq.gz -2 R2_paired.fastq.gz -o work6; then
      echo "SPAdes (work6) failed in $folder_name" >> $LOG_FILE
    fi
  else
    echo "Paired files are empty in $folder_name, skipping rnaviralspades.py work3 and SPAdes work6." >> $LOG_FILE
  fi

  # Run CollectFasta.py
  if ! python3 "$SCRIPT_DIR/CollectFasta.py"; then
    echo "CollectFasta.py failed in $folder_name" >> $LOG_FILE
    cd ..
    continue
  fi

  # Run Vigor4 using Docker
  #set -e
  #if ! docker run -u "$(id -u)":"$(id -g)" -v "$(pwd)":/working_dir -w /working_dir -m 64g --cpus="8" vigor4 bash -c "/home/vigor4/vigor4/bin/vigor4 -i contigs500.fasta -o vigor4 -d rtva"; then
  #  echo "Vigor4 failed in $folder_name" >> $LOG_FILE
  #  cd ..
  #  exit
  #fi
  #set +e

  # Run additional scripts
  #if ! bash "$SCRIPT_DIR/rotavarblast_sub.sh"; then
  #  echo "rotavarblast_sub.sh failed in $folder_name" >> $LOG_FILE
  #  cd ..
  #  continue
  #fi
  
  if ! bash "$SCRIPT_DIR/rotablast2.sh"; then
    echo "rotablast.sh failed in $folder_name" >> $LOG_FILE
  fi

  cd ..
done

output_file="blast_rotavar4.csv"
first_file=true

for dir in */; do
  file_path="${dir}blast_rota_genotyping4_updated.csv"
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
