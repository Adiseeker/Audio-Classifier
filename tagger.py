import os
import pandas as pd
import spacy
from rake_nltk import Rake
import sqlite3

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

# Path to the file containing the list of filenames
file_path = 'lista.txt'

# Read the file content
with open(file_path, 'r', encoding="utf8") as file:
    lines = file.readlines()

# Initialize lists for CSV columns
filenames = []
contents = []
keyphrases_spacy = []
keyphrases_rake = []

# Initialize RAKE
rake = Rake()


# Function to filter out pronouns and remove duplicates
def filter_keyphrases(phrases):
    unique_phrases = set()
    for phrase in phrases:
        doc = nlp(phrase)
        if not any(token.pos_ == "PRON" for token in doc):
            unique_phrases.add(phrase)
    return list(unique_phrases)


# Process each line
for line in lines:
    line = line.strip()
    # Change the extension from .wav to .txt
    txt_filename = os.path.splitext(line)[0] + '.txt'
    filenames.append(txt_filename)

    # Read content of the corresponding txt file
    try:
        with open(txt_filename, 'r', encoding="utf8") as txt_file:
            content = txt_file.read()
    except FileNotFoundError:
        content = 'File not found'

    contents.append(content)

    # Extract keyphrases using spaCy
    doc = nlp(content)
    keyphrases_spacy.append(filter_keyphrases([phrase.text for phrase in doc.noun_chunks]))

    # Extract keyphrases using RAKE
    rake.extract_keywords_from_text(content)
    keyphrases_rake.append(list(set(rake.get_ranked_phrases())))

# Create a DataFrame
df = pd.DataFrame({
    'filename': filenames,
    'content': contents,
    'keyphrases_spacy': keyphrases_spacy,
    'keyphrases_rake': keyphrases_rake
})

# Save the DataFrame to a CSV file
csv_path = 'output.csv'
df.to_csv(csv_path, index=False)

print(f"CSV file created at: {csv_path}")

# Load the CSV file into a pandas DataFrame
df = pd.read_csv(csv_path)

# Connect to (or create) the SQLite database
db_path = 'audycje.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create a table in the database
cursor.execute('''
    CREATE TABLE IF NOT EXISTS audycje (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        content TEXT,
        keyphrases_spacy TEXT,
        keyphrases_rake TEXT
    )
''')


# Function to convert list to string for storage in the database
def list_to_string(lst):
    return '; '.join(lst)


# Insert data from the DataFrame into the database
for _, row in df.iterrows():
    cursor.execute('''
        INSERT INTO audycje (filename, content, keyphrases_spacy, keyphrases_rake)
        VALUES (?, ?, ?, ?)
    ''', (row['filename'], row['content'], list_to_string(eval(row['keyphrases_spacy'])),
          list_to_string(eval(row['keyphrases_rake']))))

# Commit the transaction and close the connection
conn.commit()
conn.close()

print(f"Database created at: {db_path}")
