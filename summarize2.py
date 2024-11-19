import csv
from collections import defaultdict

# Input and output files
input_file = "blast_rota2.csv"
output_file = "blast_rota_results2.csv"

# Dictionary to store counts for each genotype
genotype_counts = defaultdict(lambda: {'count': 0, 'full': 0, 'partial': 0})

# Read the input CSV file
with open(input_file, 'r') as infile:
    reader = csv.DictReader(infile)
    
    for row in reader:
        evaluation = row['Evaluation']
        
        # Skip if the genotype is "not accepted"
        if evaluation == "not accepted":
            continue
        
        # Determine if the sequence is full or partial
        is_full = int(row['length']) >= int(row['slen'])
        
        # Update counts for the genotype
        genotype_counts[evaluation]['count'] += 1
        if is_full:
            genotype_counts[evaluation]['full'] += 1
        else:
            genotype_counts[evaluation]['partial'] += 1

# Write the summary to the output CSV file
with open(output_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    # Write headers
    writer.writerow(['Genotype', 'Total Count', 'Full Count', 'Partial Count'])
    
    # Write counts for each genotype
    for genotype, counts in genotype_counts.items():
        writer.writerow([genotype, counts['count'], counts['full'], counts['partial']])

print("Summary report has been generated:", output_file)
