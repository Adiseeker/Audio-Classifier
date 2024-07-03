import os
import pandas as pd
import spacy

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

# Path to the file
file_path = 'lista.txt'

# Read the file content
with open(file_path, 'r') as file:
    lines = file.readlines()

# Initialize lists for CSV columns
filenames = []
contents = []
keyphrases = []

# Process each line
for line in lines:
    line = line.strip()
    # Change the extension from .wav to .txt
    txt_filename = os.path.splitext(line)[0] + '.txt'
    filenames.append(txt_filename)

    # Read content of the corresponding txt file
    try:
        with open(txt_filename, 'r') as txt_file:
            content = txt_file.read()
    except FileNotFoundError:
        content = 'File not found'

    # Extract keyphrases using spaCy
    doc = nlp(content)
    keyphrases.append([phrase.text for phrase in doc.noun_chunks])

    contents.append(content)

# Create a DataFrame
df = pd.DataFrame({
    'filename': filenames,
    'content': contents,
    'keyphrases': keyphrases
})

# Save the DataFrame to a CSV file
csv_path = 'output.csv'
df.to_csv(csv_path, index=False)

print(f"CSV file created at: {csv_path}")
