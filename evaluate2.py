import csv

# Define thresholds
base_thresholds = {'G': 80, 'P': 80, 'I': 85, 'R': 83, 'C': 84, 
                   'M': 81, 'A': 79, 'N': 85, 'T': 85, 'E': 85, 'H': 91}
min_lengths = {'G': 500, 'P': 1163, 'I': 596, 'R': 1632, 'C': 1319,
               'M': 1253, 'A': 740, 'N': 500, 'T': 500, 'E': 500, 'H': 500}

# Read the BLAST results and write to new CSV with evaluation
input_file = "blast_rota2.txt"
output_file = "blast_rota2.csv"

with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(infile, delimiter='\t')
    writer = csv.writer(outfile)
    
    # Write headers
    writer.writerow(['qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen', 
                     'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore', 'sstrand', 
                     'slen', 'Evaluation'])
    
    for row in reader:
        qseqid, sseqid, pident, length = row[0], row[1], float(row[2]), int(row[3])
        genotype = sseqid.split('|')[0]
        gene, number = genotype[0], genotype[1:]  # Extract the gene and its number

        # Determine if full or partial
        is_full = int(length) >= int(row[13])
        
        # Adjust threshold based on full/partial status
        threshold = base_thresholds[gene] if is_full else base_thresholds[gene] + 2
        
        # Evaluate based on pident and length (for partial sequences)
        if pident >= threshold and (is_full or length >= min_lengths[gene]):
            evaluation = genotype  # Accepted
        else:
            evaluation = "not accepted"  # Not accepted
        
        # Write the row with the evaluation column
        writer.writerow(row + [evaluation])

print("Genotyping report has been generated:", output_file)
