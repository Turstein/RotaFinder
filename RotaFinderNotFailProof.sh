#!/bin/bash

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
  # Change into directory
  echo "changing to directory: $dir"
  cd "$dir" || continue
  folder_name=$(basename "$dir")
  
  trimmomatic PE *_R1_001.fastq.gz *_R2_001.fastq.gz R1_paired.fastq.gz R1_unpaired.fastq.gz R2_paired.fastq.gz R2_unpaired.fastq.gz ILLUMINACLIP:"$SCRIPT_DIR/adapters.fa":2:30:10:1 SLIDINGWINDOW:3:15 LEADING:3 TRAILING:3 MINLEN:36
  
  
  bbnorm.sh in1=R1_paired.fastq.gz in2=R2_paired.fastq.gz out1=R1bbnorm.fastq.gz out2=R2bbnorm.fastq.gz target=100 min=5
  bbnorm.sh in1=R1_paired.fastq.gz in2=R2_paired.fastq.gz out1=R1bbnorm2.fastq.gz out2=R2bbnorm2.fastq.gz target=500 min=5
 
  rnaviralspades.py -t 12 -1 R1bbnorm.fastq.gz -2 R2bbnorm.fastq.gz  -o work1
  rnaviralspades.py -t 12 -1 R1bbnorm2.fastq.gz -2 R2bbnorm2.fastq.gz  -o work2
  rnaviralspades.py -t 12 -1 R1_paired.fastq.gz -2 R2_paired.fastq.gz  -o work3
  spades.py -t 12 --isolate --cov-cutoff auto -1 R1_paired.fastq.gz -2 R2_paired.fastq.gz -o work6 


  python3 "$SCRIPT_DIR/CollectFasta.py"
  
  docker run -u $(id -u):$(id -g) -v "$(pwd)":/working_dir -w /working_dir -m 64g --cpus="8" vigor4 bash -c "/home/vigor4/vigor4/bin/vigor4 -i contigs500.fasta -o vigor4 -d rtva"

  bash "$SCRIPT_DIR/rotavarblast_sub.sh"
  bash "$SCRIPT_DIR/rotablast.sh"

  cd ..
done



# Define the output file
output_file="blast_rotavar.csv"

# Initialize output file and add header
first_file=true

# Loop through directories one level down in pwd
for dir in */; do
  # Check if the file exists in the directory
  file_path="${dir}blast_rota_genotyping.csv"
  if [[ -f "$file_path" ]]; then
    if $first_file; then
      # Copy the header and data if it's the first file
      cat "$file_path" > "$output_file"
      first_file=false
    else
      # Skip the header and append data from subsequent files
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
