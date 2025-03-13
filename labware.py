import csv, re

with open('blast_rotavar4.csv', newline='') as infile, open('LabwareReportFromRotaFinder1.csv', 'w', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames + ['LabwareGenotype', 'Art']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        genotype = row['Genotype']
        parts = genotype.split('-')
        labware = '-'.join(parts[:2]) if len(parts) >= 2 else genotype
        row['LabwareGenotype'] = labware

        # Default to "Utilstrekkelig sekvens"
        art = "Utilstrekkelig sekvens"
        if '-' in labware:
            g_part, p_part = labware.split('-', 1)
            # Check if g_part starts with 'G' followed by digits
            if re.fullmatch(r'G\d+', g_part):
                # p_part should be 'P' followed by digits or P[digit(s)] in square brackets
                if re.fullmatch(r'P\d+', p_part) or re.fullmatch(r'P\[\d+\]', p_part):
                    art = "Rotavirus alphagastroenteritidis"
        row['Art'] = art
        writer.writerow(row)