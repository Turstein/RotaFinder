import csv
from collections import defaultdict

# Input and output files
input_file = "blast_rota2.csv"
output_file = "blast_rota_results2.csv"

# Function to extract COV value from qseqid
def get_coverage(qseqid):
    try:
        parts = qseqid.split("cov_")
        cov_value = float(parts[1].split("_")[0])  # Assumes format "cov_<value>_"
        return cov_value
    except (IndexError, ValueError):
        return 0  # Return 0 if coverage parsing fails

# Dictionary to store counts for each genotype
genotype_counts = defaultdict(lambda: {
    'count': 0,
    'full': 0,
    'partial': 0,
    'high_cov_full': 0,
    'low_cov_full': 0,
    'high_cov_partial': 0,
    'low_cov_partial': 0
})

# Read the input CSV file
with open(input_file, 'r') as infile:
    reader = csv.DictReader(infile)
    
    for row in reader:
        evaluation = row['Evaluation']
        qseqid = row['qseqid']
        
        # Skip if the genotype is "not accepted"
        if evaluation == "not accepted":
            continue
        
        # Extract COV from qseqid
        cov = get_coverage(qseqid)
        
        # Determine if the sequence is full or partial
        is_full = int(row['length']) >= int(row['slen'])
        
        # Update counts for the genotype
        genotype_counts[evaluation]['count'] += 1
        if is_full:
            genotype_counts[evaluation]['full'] += 1
            if cov >= 10:
                genotype_counts[evaluation]['high_cov_full'] += 1
            else:
                genotype_counts[evaluation]['low_cov_full'] += 1
        else:
            genotype_counts[evaluation]['partial'] += 1
            if cov >= 10:
                genotype_counts[evaluation]['high_cov_partial'] += 1
            else:
                genotype_counts[evaluation]['low_cov_partial'] += 1

# Write the summary to the output CSV file
with open(output_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    # Write headers
    writer.writerow([
        'Genotype', 
        'Total Count', 
        'Full Count', 
        'Partial Count', 
        'High COV Count Full', 
        'Low COV Count Full', 
        'High COV Count Partial', 
        'Low COV Count Partial'
    ])
    
    # Write counts for each genotype
    for genotype, counts in genotype_counts.items():
        writer.writerow([
            genotype,
            counts['count'],
            counts['full'],
            counts['partial'],
            counts['high_cov_full'],
            counts['low_cov_full'],
            counts['high_cov_partial'],
            counts['low_cov_partial']
        ])

print("Summary report has been generated:", output_file)
