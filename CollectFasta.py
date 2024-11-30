import os

# Define the mapping of directories to specific text
folder_text = {
    'work1': '_bbnorm100rnaviralspades',
    'work2': '_bbnorm500rnaviralspades',
    'work3': '_rnaviralspades',
    'work6': '_spadesIsolateAutocutoff',
    'work7': '_clumpifyrnaviralspades'
}

output_file = 'contigs.fasta'

# Open the output file for writing
with open(output_file, 'w') as outfile:
    # Process each directory and its corresponding file
    for folder, text in folder_text.items():
        # Path to the FASTA file in the folder
        fasta_path = os.path.join(folder, 'contigs.fasta')
        
        # Check if the FASTA file exists
        if os.path.exists(fasta_path):
            with open(fasta_path, 'r') as infile:
                # Process each line in the file
                for line in infile:
                    line = line.strip()  # Remove trailing newline characters
                    if line.startswith('>'):  # Header line
                        # Write the header line with appended text to the output file
                        outfile.write(line + '' + text + '\n')
                    elif line:  # Sequence line, check if not empty
                        # Write the sequence line to the output file
                        outfile.write(line + '\n')
        else:
            print(f"File not found: {fasta_path}")

print(f"Processed FASTA sequences written to {output_file}")

from Bio import SeqIO

# Input and output file names
input_file = "contigs.fasta"
output_file2 = "contigs500.fasta"

# Filter sequences and write to output file
with open(output_file2, "w") as output_handle:
    for record in SeqIO.parse(input_file, "fasta"):
        if len(record.seq) >= 500:
            SeqIO.write(record, output_handle, "fasta")
