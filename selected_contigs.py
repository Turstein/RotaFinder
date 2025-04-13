#!/usr/bin/env python3
import csv

# File names
blast_csv = "blast_rota2.csv"
input_fasta = "contigs500_COV.fasta"
output_fasta = "selected_contigs.fasta"

def get_coverage(qseqid):
    """
    Extracts the coverage value from a qseqid.
    Expected format: containing 'cov_<value>_'.
    Returns 0 if extraction fails.
    """
    try:
        parts = qseqid.split("cov_")
        cov_value = float(parts[1].split("_")[0])
        return cov_value
    except (IndexError, ValueError):
        return 0

# Dictionaries to store candidate contig for each genotype.
# full_candidates holds full-length contigs (length >= slen) along with their qseqid and coverage.
# partial_candidates holds partial contigs (length < slen) along with their qseqid and length.
full_candidates = {}
partial_candidates = {}

# Read the blast CSV and store the best candidate for full and partial contigs.
with open(blast_csv, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        genotype = row['Evaluation']
        if genotype == "not accepted":
            continue  # Skip not-accepted genotypes

        try:
            length = int(row['length'])
            slen = int(row['slen'])
        except ValueError:
            continue  # Skip rows if conversion fails

        qseqid = row['qseqid']
        cov = get_coverage(qseqid)

        # If the contig is full-length:
        if length >= slen:
            # If this genotype hasn't been encountered yet for a full contig, add it.
            if genotype not in full_candidates:
                full_candidates[genotype] = {'qseqid': qseqid, 'coverage': cov}
            else:
                current_cov = full_candidates[genotype]['coverage']
                current_is_high = current_cov >= 10
                new_is_high = cov >= 10
                # Prefer a high-coverage candidate over a low-coverage candidate.
                if current_is_high and not new_is_high:
                    continue
                elif not current_is_high and new_is_high:
                    full_candidates[genotype] = {'qseqid': qseqid, 'coverage': cov}
                else:
                    # If both candidates are in the same category, pick the one with higher coverage.
                    if cov > current_cov:
                        full_candidates[genotype] = {'qseqid': qseqid, 'coverage': cov}
        else:
            # Contig is partial. Choose the one with the greatest length.
            if genotype not in partial_candidates:
                partial_candidates[genotype] = {'qseqid': qseqid, 'length': length}
            else:
                if length > partial_candidates[genotype]['length']:
                    partial_candidates[genotype] = {'qseqid': qseqid, 'length': length}

# Combine candidates: for each genotype, if a full candidate is available use it;
# otherwise, if there is a partial candidate use that.
selected_candidates = {}
all_genotypes = set(full_candidates.keys()).union(set(partial_candidates.keys()))
for genotype in all_genotypes:
    if genotype in full_candidates:
        selected_candidates[genotype] = {'qseqid': full_candidates[genotype]['qseqid'], 'type': 'full'}
    elif genotype in partial_candidates:
        selected_candidates[genotype] = {'qseqid': partial_candidates[genotype]['qseqid'], 'type': 'partial'}

# Load sequences from the input FASTA file into a dictionary.
# The key is derived from the FASTA header (first token after '>').
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

# Write selected contigs to a new FASTA file.
with open(output_fasta, 'w') as outfile:
    for genotype, candidate in selected_candidates.items():
        qseqid = candidate['qseqid']
        candidate_type = candidate['type']  # 'full' or 'partial'
        if qseqid in fasta_records:
            original_header, sequence = fasta_records[qseqid]
            # Modify header based on candidate type.
            if candidate_type == 'partial':
                new_header = f">{genotype}_PARTIAL_{original_header[1:]}"
            else:
                new_header = f">{genotype}_{original_header[1:]}"
            outfile.write(new_header + "\n")
            # Write the sequence in lines of up to 70 characters.
            for i in range(0, len(sequence), 70):
                outfile.write(sequence[i:i+70] + "\n")
        else:
            print(f"Warning: qseqid {qseqid} not found in FASTA file.")

print("Selected contigs have been written to:", output_fasta)
