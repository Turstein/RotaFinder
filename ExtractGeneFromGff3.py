import sys
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

def extract_sequences(name, thresholds, orf_lengths):
    try:
        # Set the thresholds for the current gene, or use default values if not specified
        lower_threshold, upper_threshold = thresholds.get(name, (100, 10000))  # Default thresholds
        orf_length = orf_lengths.get(name, 0)  # Expected ORF length for the gene

        with open("vigor4.gff3") as gff_file, open("contigs.fasta") as fasta_file:
            sequences = SeqIO.parse(fasta_file, "fasta")
            fasta_dict = {seq.id: seq for seq in sequences}

            seq_diffs = []
            orf_statuses = []
            has_full_entries = False  # Track if we encounter any full (non-partial) sequences

            for line in gff_file:
                columns = line.strip().split("\t")
                if len(columns) < 9:
                    continue

                if "Name=" + name in columns[8]:
                    # Check if the entry is marked as "Partial"
                    is_partial = "Partial" in columns[8]
                    if not is_partial:
                        has_full_entries = True  # Found a full (non-partial) entry

            # Reset file reading position
            gff_file.seek(0)

            for line in gff_file:
                columns = line.strip().split("\t")
                if len(columns) < 9:
                    continue

                if "Name=" + name in columns[8]:
                    seqid = columns[0]
                    start_pos = int(columns[3]) - 1  # Convert to 0-based index
                    end_pos = int(columns[4])
                    strand = columns[6]
                    is_partial = "Partial" in columns[8]

                    # Include sequence only if it is full, or if there are no full entries
                    if not has_full_entries or not is_partial:
                        if seqid in fasta_dict:
                            full_sequence = fasta_dict[seqid]
                            gene_sequence = full_sequence.seq[start_pos:end_pos]  # Slice to get gene sequence

                            if strand == "-":
                                gene_sequence = gene_sequence.reverse_complement()

                            new_seq_record = SeqRecord(gene_sequence,
                                                       id=full_sequence.id,
                                                       description=full_sequence.description.replace(seqid + " ", "", 1))

                            gene_length = len(gene_sequence)
                            
                            # Filter based on thresholds
                            if lower_threshold <= gene_length <= upper_threshold:
                                # Add the sequence to the list for final output
                                seq_diffs.append(new_seq_record)

                                # Determine if the gene is Full or Partial
                                if orf_length - 3 <= gene_length <= orf_length + 3:
                                    orf_statuses.append("F")  # Full
                                else:
                                    orf_statuses.append("P")  # Partial
                        else:
                            print(f"Sequence ID {seqid} not found in FASTA file")

            # Sort sequences by length in descending order
            seq_diffs.sort(key=lambda x: len(x.seq), reverse=True)

            # Save all sequences in a single file
            output_file = f"output_{name}.fasta"
            with open(output_file, "w") as out_file:
                SeqIO.write(seq_diffs, out_file, "fasta")

            # Save the ORF status in a separate file
            orf_output_file = f"output_{name}.ORF"
            with open(orf_output_file, "w") as orf_file:
                for status in orf_statuses:
                    orf_file.write(f"{status}\n")

    except FileNotFoundError:
        print("One of the files was not found. Please check the file paths.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
        
        # Define thresholds for each gene here with lower and upper bounds
        thresholds = {
            "VP7": (500, 1308),
            "VP4": (1163, 3100),
            "VP6": (596, 1588),
            "VP1": (1632, 4352),
            "VP2": (1319, 3588),
            "VP3": (1253, 3340),
            "NSP1": (740, 1988),
            "NSP2": (500, 1268),
            "NSP3": (500, 1256),
            "NSP4": (500, 736),
            "NSP5": (500, 800)
            # Add more gene names and their thresholds as needed
        }
        
        # Define expected ORF lengths for each gene
        orf_lengths = {
            "VP1": 3264,
            "VP2": 2637,
            "VP3": 2505,
            "VP4": 2325,
            "NSP1": 1479,
            "VP6": 1191,
            "NSP3": 939,
            "NSP2": 951,
            "VP7": 978,
            "NSP4": 525,
            "NSP5": 600
        }
        
        extract_sequences(name, thresholds, orf_lengths)
    else:
        print("Please provide the gene name parameter.")