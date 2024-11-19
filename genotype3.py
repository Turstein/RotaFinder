import csv
import os

# Input and output files
input_file = "blast_rota_results2.csv"
output_file = "blast_rota_genotyping3.csv"

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
        full_count = int(row['Full Count'])
        partial_count = int(row['Partial Count'])
        
        # Extract gene letter and number
        gene_letter = ''.join([char for char in genotype if char.isalpha()])[0]  # Assumes single-letter gene
        gene_number = ''.join([char for char in genotype if char.isdigit()])
        
        # Store the gene number, full count, and partial count in the appropriate list
        genotype_data[gene_letter].append({
            'genotype': gene_number,
            'full_count': full_count,
            'partial_count': partial_count
        })

# Process each gene to select the main genotype and any additional ones
final_genotype = []
extra_info = []

for gene in gene_order:
    if genotype_data[gene]:
        # Find the maximum full count for this gene
        max_full = max(item['full_count'] for item in genotype_data[gene])
        
        # Find all genotypes with the maximum full count
        top_genotypes = [item for item in genotype_data[gene] if item['full_count'] == max_full]
        
        if max_full == 0:
            # No full counts, use maximum partial count
            max_partial = max(item['partial_count'] for item in genotype_data[gene])
            top_partial_genotypes = [item for item in genotype_data[gene] if item['partial_count'] == max_partial]
            
            if len(top_partial_genotypes) == 1:
                # Unique main genotype based on partial count
                main_genotype = top_partial_genotypes[0]['genotype']
                if gene == 'P':
                    final_genotype.append(f"{gene}[{main_genotype}]")
                else:
                    final_genotype.append(f"{gene}{main_genotype}")
            else:
                # Tie in partial count
                final_genotype.append(f"{gene}?")
                tied_genotypes = [f"{gene}{item['genotype']}" for item in top_partial_genotypes]
                extra_info.extend(tied_genotypes)
        else:
            # Resolve ties with full count using partial count
            if len(top_genotypes) == 1:
                # Unique main genotype
                main_genotype = top_genotypes[0]['genotype']
                if gene == 'P':
                    final_genotype.append(f"{gene}[{main_genotype}]")
                else:
                    final_genotype.append(f"{gene}{main_genotype}")
            else:
                # Tie in full count, resolve with partial count
                max_partial_in_full = max(item['partial_count'] for item in top_genotypes)
                top_partial_genotypes = [
                    item for item in top_genotypes if item['partial_count'] == max_partial_in_full
                ]
                
                if len(top_partial_genotypes) == 1:
                    # Unique main genotype after resolving partial count tie
                    main_genotype = top_partial_genotypes[0]['genotype']
                    if gene == 'P':
                        final_genotype.append(f"{gene}[{main_genotype}]")
                    else:
                        final_genotype.append(f"{gene}{main_genotype}")
                else:
                    # Still a tie after partial count, mark as '?' and add to extra_info
                    final_genotype.append(f"{gene}?")
                    tied_genotypes = [f"{gene}{item['genotype']}" for item in top_partial_genotypes]
                    extra_info.extend(tied_genotypes)

            # Add other genotypes to extra_info
            other_genotypes = [f"{gene}{item['genotype']}" for item in genotype_data[gene] 
                               if item['genotype'] not in [g['genotype'] for g in top_genotypes]]
            extra_info.extend(other_genotypes)
    else:
        # If gene not found, mark as missing ("X")
        final_genotype.append(f"{gene}X")

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

# Check if all main genotypes are 'X'
all_genotypes_are_missing = all(gt.endswith('X') for gt in final_genotype)

if all_genotypes_are_missing:
    # Set Genotype column to empty and Extra Information to "None"
    genotype_string = ""
    extra_info_string = "None"

# Write the result to the output file
with open(output_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Folder Name', 'Genotype', 'Extra Information'])
    writer.writerow([folder_name, genotype_string, extra_info_string])

print("Genotyping report has been generated:", output_file)
