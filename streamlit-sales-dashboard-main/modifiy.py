import pandas as pd

# Load your dataset
df = pd.read_csv('output.csv')

# Define a mapping for region replacements
region_mapping = {
    'Regional Implementation & Operations 1': 'RIO-1',
    'Regional Implementation & Operations 2': 'RIO-2',
    'Regional Implementation & Operations 3': 'RIO-3',
    'Regional Implementation & Operations 4': 'RIO-4'
    # Add more mappings if needed
}

# Replace values in the 'Region' column based on the mapping
df['Region'] = df['Region'].replace(region_mapping)

# Save the updated DataFrame to a new CSV file or overwrite the existing one
df.to_csv('output_updated.csv', index=False)

