from Bio import SeqIO

# Input and output file names
INPUT_FASTA = "contigs500.fasta"
OUTPUT_FASTA = "contigs500_COV.fasta"

# Function to parse coverage from the FASTA header
def get_coverage(header):
    try:
        # Extract the coverage value from the header
        parts = header.split("cov_")
        cov_value = float(parts[1].split("_")[0])  # Assumes format "cov_<value>_"
        return cov_value
    except (IndexError, ValueError):
        return 0  # Return 0 if coverage parsing fails

# Filter sequences and write to output
with open(OUTPUT_FASTA, "w") as output_handle:
    for record in SeqIO.parse(INPUT_FASTA, "fasta"):
        coverage = get_coverage(record.description)
        if coverage >= 3:
            SeqIO.write(record, output_handle, "fasta")

print(f"Filtered FASTA file has been saved as {OUTPUT_FASTA}.")
