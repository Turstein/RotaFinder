import csv
import os

# Input and output files
input_file = "blast_rota_results.csv"
output_file = "blast_rota_genotyping.csv"

# List of gene letters in desired order
gene_order = ['G', 'P', 'I', 'R', 'C', 'M', 'A', 'N', 'T', 'E', 'H']

# Get the folder name where the output file is created
folder_name = os.path.basename(os.getcwd())

# Dictionary to store genotype information
genotype_data = {gene: [] for gene in gene_order}

# Read the input CSV and populate genotype data
with open(input_file, 'r', newline='') as infile:
    reader = csv.DictReader(infile)
    for row in reader:
        genotype = row['Genotype']
        total_count = int(row['Total Count'])
        
        # Extract gene letter and number
        gene_letter = ''.join([char for char in genotype if char.isalpha()])[0]  # Assumes single-letter gene
        gene_number = ''.join([char for char in genotype if char.isdigit()])
        
        # Store the gene number and total count in the appropriate list
        genotype_data[gene_letter].append({
            'genotype': gene_number,
            'total_count': total_count
        })

# Process each gene to select the main genotype and any additional ones
final_genotype = []
extra_info = []

for gene in gene_order:
    if genotype_data[gene]:
        # Find the maximum total count for this gene
        max_total = max(item['total_count'] for item in genotype_data[gene])
        
        # Find all genotypes with the maximum total count
        top_genotypes = [item['genotype'] for item in genotype_data[gene] if item['total_count'] == max_total]
        
        if len(top_genotypes) == 1:
            # Unique main genotype
            main_genotype = top_genotypes[0]
            if gene == 'P':
                final_genotype.append(f"{gene}[{main_genotype}]")
            else:
                final_genotype.append(f"{gene}{main_genotype}")
            
            # Add all other genotypes to extra_info
            other_genotypes = [f"{gene}{item['genotype']}" for item in genotype_data[gene] 
                               if item['genotype'] != main_genotype]
            extra_info.extend(other_genotypes)
        else:
            # Tie detected
            final_genotype.append(f"{gene}?")
            
            # Add all genotypes to extra_info
            tied_genotypes = [f"{gene}{gt}" for gt in [item['genotype'] for item in genotype_data[gene]]]
            extra_info.extend(tied_genotypes)
    else:
        # If gene not found, add a question mark
        final_genotype.append(f"{gene}?")

# Remove duplicates and sort extra information based on gene_order and genotype number
def sort_key(genotype_str):
    gene = genotype_str[0]
    number = ''.join(filter(str.isdigit, genotype_str))
    # Convert number to integer for proper sorting
    try:
        number = int(number)
    except ValueError:
        number = 0
    return (gene_order.index(gene) if gene in gene_order else len(gene_order), number)

unique_extra_info = sorted(set(extra_info), key=sort_key)

# Create the final strings for genotype and extra info
genotype_string = "-".join(final_genotype)
extra_info_string = "; ".join(unique_extra_info) if unique_extra_info else "None"

# Check if all main genotypes are '?'
all_genotypes_are_unknown = all(gt.endswith('?') for gt in final_genotype)

if all_genotypes_are_unknown:
    # Set Genotype column to empty and Extra Information to "None"
    genotype_string = ""
    extra_info_string = "None"

# Write the result to the output file
with open(output_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Folder Name', 'Genotype', 'Extra Information'])
    writer.writerow([folder_name, genotype_string, extra_info_string])

print("Genotyping report has been generated:", output_file)
