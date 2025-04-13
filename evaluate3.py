import csv

# Define thresholds
base_thresholds = {
    'G': 80, 'P': 80, 'I': 85, 'R': 83, 'C': 84, 
    'M': 81, 'A': 79, 'N': 85, 'T': 85, 'E': 85, 'H': 91
}
min_lengths = {
    'G': 500, 'P': 1163, 'I': 596, 'R': 1632, 'C': 1319,
    'M': 1253, 'A': 740, 'N': 500, 'T': 500, 'E': 500, 'H': 500
}

# Read the BLAST results and write to new CSV with evaluation
input_file = "blast_rota2.txt"
output_file = "blast_rota2.csv"

with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(infile, delimiter='\t')
    writer = csv.writer(outfile)
    
    # Write headers
    writer.writerow([
        'qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen', 
        'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore', 'sstrand', 
        'slen', 'Evaluation'
    ])
    
    for row in reader:
        qseqid = row[0]
        sseqid = row[1]
        pident = float(row[2])
        length = int(row[3])
        
        # Extract genotype information from the subject id (assumes format like "G123|...")
        genotype = sseqid.split('|')[0]
        gene = genotype[0]
        # The 'number' part is extracted but not used further:
        number = genotype[1:]  

        # Determine if the alignment is full-length based on alignment length vs. subject sequence length (slen is assumed at row[13])
        is_full = length >= int(row[13])
        
        # Adjust threshold: full-length hits use the base threshold,
        # partial hits require a stricter (base + 2) threshold.
        threshold = base_thresholds[gene] if is_full else base_thresholds[gene] + 2

        # Evaluate based on pident and length.
        # First check that the alignment meets the length criteria.
        if is_full or length >= min_lengths[gene]:
            if pident >= threshold:
                evaluation = genotype  # Accepted, meets both criteria.
            else:
                # Length criteria fulfilled, but percent identity is below cutoff.
                evaluation = f"{genotype}0000{pident}"
        else:
            evaluation = "not accepted"  # Length criteria not met.
        
        # Write the original row with the added Evaluation column.
        writer.writerow(row + [evaluation])

print("Genotyping report has been generated:", output_file)
