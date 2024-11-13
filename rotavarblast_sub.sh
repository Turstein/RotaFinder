#!/bin/bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate rotavar
# Get the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# List of genes to process
genes=("VP7" "VP4" "VP6" "VP1" "VP2" "VP3" "NSP1" "NSP2" "NSP3" "NSP4" "NSP5")

# Loop through each gene in the list
for gene in "${genes[@]}"
do
    echo "Processing $gene"
    if ! python3 "$SCRIPT_DIR/ExtractGeneFromGff3.py" "$gene"; then
        echo "Failed to extract gene data for $gene"
        exit 1
    fi
    


    
    #echo "Finished processing $gene"
done


rm -r work1
rm -r work2
rm -r work3
rm -r work6
rm R1bbnorm.fastq.gz
rm R1bbnorm2.fastq.gz
rm R2bbnorm.fastq.gz
rm R2bbnorm2.fastq.gz
rm R1_paired.fastq.gz
rm R1_unpaired.fastq.gz
rm R2_paired.fastq.gz
rm R2_unpaired.fastq.gz