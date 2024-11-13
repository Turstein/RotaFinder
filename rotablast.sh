#!/bin/bash

# Activate the initial conda environment
source /home/torstein.gjolgali.frengen/miniconda3/etc/profile.d/conda.sh
#source ~/miniconda3/etc/profile.d/conda.sh
conda activate rotavar
# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cat output_VP1.fasta output_VP2.fasta output_VP3.fasta output_VP4.fasta output_VP6.fasta output_VP7.fasta output_NSP1.fasta output_NSP2.fasta output_NSP3.fasta output_NSP4.fasta output_NSP5.fasta > contigs_rota.fasta

# Set the minimum sequence length to be considered (adjust if necessary)
MIN_SEQ_LENGTH=500

# Input and output files
INPUT_FASTA="contigs_rota.fasta"
BLAST_DB="$SCRIPT_DIR/241112_rotadb"
BLAST_OUTPUT="blast_rota.txt"



# Check if input FASTA exists
if [ ! -f "$INPUT_FASTA" ]; then
    echo "Error: $INPUT_FASTA not found."
    exit 1
fi

# Count the total number of sequences in contigs.fasta
TOTAL_SEQUENCES=$(grep -c "^>" "$INPUT_FASTA")

# Run BLAST 
blastn -query "$INPUT_FASTA" -db "$BLAST_DB" -out "$BLAST_OUTPUT" \
  -outfmt "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore sstrand slen" \
  -max_target_seqs 1 -strand both
if [ ! -f "$BLAST_OUTPUT" ]; then
    echo "Error: BLAST did not create $BLAST_OUTPUT. Exiting."
    exit 1
fi

python3 "$SCRIPT_DIR/evaluate.py"
python3 "$SCRIPT_DIR/summarize.py"
python3 "$SCRIPT_DIR/genotype.py"