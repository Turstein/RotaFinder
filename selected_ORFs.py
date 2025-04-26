#!/usr/bin/env python3
import csv

# File names
blast_csv = "blast_rota2.csv"
input_fasta = "contigs500_COV.fasta"
output_fasta = "selected_ORFs.fasta"

def get_coverage(qseqid):
    """
    Extracts coverage value from qseqid.
    Expected format: a substring like 'cov_<value>_'.
    Returns 0 if parsing fails.
    """
    try:
        parts = qseqid.split("cov_")
        cov_value = float(parts[1].split("_")[0])
        return cov_value
    except (IndexError, ValueError):
        return 0

def reverse_complement(seq):
    """Return the reverse complement of a DNA sequence."""
    # Define mapping for nucleotides.
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G',
                  'a': 't', 't': 'a', 'g': 'c', 'c': 'g',
                  'N': 'N', 'n': 'n'}
    return "".join(complement.get(base, base) for base in reversed(seq))

# Dictionaries for candidate selection.
# For each genotype, we keep separate candidate info for full and partial contigs.
full_candidates = {}
partial_candidates = {}

with open(blast_csv, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        genotype = row['Evaluation']
        if genotype == "not accepted":
            continue  # Skip unaccepted genotypes
        
        try:
            length = int(row['length'])
            slen = int(row['slen'])
            qstart = int(row['qstart'])
            qend = int(row['qend'])
        except ValueError:
            continue  # Skip any rows with invalid numerical fields
        
        qseqid = row['qseqid']
        cov = get_coverage(qseqid)
        sstrand = row.get('sstrand', '+')
        
        # Full candidate: contig where length >= slen.
        if length >= slen:
            candidate_info = {
                'qseqid': qseqid,
                'coverage': cov,
                'qstart': qstart,
                'qend': qend,
                'sstrand': sstrand
            }
            if genotype not in full_candidates:
                full_candidates[genotype] = candidate_info
            else:
                # Prefer a candidate with high coverage (>=10) over a low one.
                current_cov = full_candidates[genotype]['coverage']
                current_is_high = current_cov >= 10
                new_is_high = cov >= 10
                if current_is_high and not new_is_high:
                    continue
                elif not current_is_high and new_is_high:
                    full_candidates[genotype] = candidate_info
                else:
                    # When both are of the same quality, choose the one with higher coverage.
                    if cov > current_cov:
                        full_candidates[genotype] = candidate_info
        else:
            # Partial candidate: choose the contig with the largest length.
            candidate_info = {
                'qseqid': qseqid,
                'length': length,
                'qstart': qstart,
                'qend': qend,
                'sstrand': sstrand
            }
            if genotype not in partial_candidates:
                partial_candidates[genotype] = candidate_info
            else:
                if length > partial_candidates[genotype]['length']:
                    partial_candidates[genotype] = candidate_info

# Consolidate selected candidate for each genotype.
selected_candidates = {}
all_genotypes = set(full_candidates.keys()).union(set(partial_candidates.keys()))
for genotype in all_genotypes:
    if genotype in full_candidates:
        candidate = full_candidates[genotype]
        candidate['type'] = 'full'
        selected_candidates[genotype] = candidate
    elif genotype in partial_candidates:
        candidate = partial_candidates[genotype]
        candidate['type'] = 'partial'
        selected_candidates[genotype] = candidate

# Parse the FASTA file into a dictionary.
# Keys are the qseqids (extracted from the header’s first token, removing the '>' character).
fasta_records = {}
with open(input_fasta, 'r') as f:
    header = None
    seq_lines = []
    for line in f:
        line = line.strip()
        if line.startswith(">"):
            if header:
                key = header.split()[0][1:]
                fasta_records[key] = (header, "".join(seq_lines))
            header = line
            seq_lines = []
        else:
            seq_lines.append(line)
    if header:
        key = header.split()[0][1:]
        fasta_records[key] = (header, "".join(seq_lines))

# Write the selected ORFs to the output FASTA file.
with open(output_fasta, 'w') as outfile:
    for genotype, candidate in selected_candidates.items():
        qseqid = candidate['qseqid']
        candidate_type = candidate['type']  # 'full' or 'partial'
        if qseqid not in fasta_records:
            print(f"Warning: qseqid {qseqid} not found in FASTA file.")
            continue
        
        original_header, full_seq = fasta_records[qseqid]
        # Extract the ORF from the full sequence:
        # Convert qstart, qend from 1-indexed (inclusive) to Python’s 0-indexed slicing.
        qstart = candidate['qstart']
        qend = candidate['qend']
        orf_seq = full_seq[qstart-1:qend]
        
        # Reverse-complement if sstrand is '-' (ignoring extra spaces)
        if candidate['sstrand'].strip() == 'minus':
            orf_seq = reverse_complement(orf_seq)
        
        # Create a new header:
        # For full candidates: >genotype_ORF_originalHeader
        # For partial candidates: >genotype_PARTIAL_ORF_originalHeader
        if candidate_type == 'partial':
            new_header = f">{genotype}_PARTIAL_ORF_{original_header[1:]}"
        else:
            new_header = f">{genotype}_ORF_{original_header[1:]}"
        
        outfile.write(new_header + "\n")
        # Write the sequence in 70-character lines.
        for i in range(0, len(orf_seq), 70):
            outfile.write(orf_seq[i:i+70] + "\n")

print("Selected ORF sequences have been written to:", output_fasta)
