import pandas as pd

# Read the input CSV files
genotyping_df = pd.read_csv('blast_rota_genotyping4.csv')
blast_df = pd.read_csv('blast_rota2.csv')

# Initialize the new columns with empty strings
genotyping_df['Rotarix VP7'] = ''
genotyping_df['Rotarix VP4'] = ''

# Function to compute average pident for given criteria
def compute_average_pident(df, evaluation_value):
    # Filter based on 'Evaluation' and 'sseqid' containing 'Vaccine'
    filtered = df[
        (df['Evaluation'] == evaluation_value) &
        (df['sseqid'].str.contains('Vaccine', case=False, na=False))
    ]
    if not filtered.empty:
        # Calculate the average 'pident'
        return filtered['pident'].mean()
    else:
        return ''

# Process each row in the genotyping DataFrame
for index, row in genotyping_df.iterrows():
    # Since there's no direct mapping, we'll use the entire blast_df
    vp7_avg_pident = compute_average_pident(blast_df, 'G1')
    vp4_avg_pident = compute_average_pident(blast_df, 'P8')
    # Assign the computed averages to the new columns
    genotyping_df.at[index, 'Rotarix VP7'] = vp7_avg_pident
    genotyping_df.at[index, 'Rotarix VP4'] = vp4_avg_pident

# Save the updated DataFrame to a new CSV file
genotyping_df.to_csv('blast_rota_genotyping4_updated.csv', index=False)
