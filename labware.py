import csv, re

with open('blast_rotavar4.csv', newline='') as infile, open('Labware.csv', 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ['LabwareGenotype', 'Art']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        genotype = row['Genotype']
        parts = genotype.split('-')
        labware = '-'.join(parts[:2]) if len(parts) >= 2 else genotype
        row['LabwareGenotype'] = labware

        art = ""
        if '-' in labware:
            g_part, p_part = labware.split('-', 1)
            # Check if G is followed by a number.
            if re.fullmatch(r'G\d+', g_part):
                # P can be either P followed by digits or P[digits]
                if re.fullmatch(r'P\d+', p_part) or re.fullmatch(r'P\[\d+\]', p_part):
                    art = "Rotavirus alphagastroenteritidis"
        row['Art'] = art
        writer.writerow(row)
