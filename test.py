import sqlite3
from keybert import KeyBERT

# Initialize KeyBERT with embeddings
kw_model = KeyBERT(model='paraphrase-mpnet-base-v2')  # You can choose different models

# Connect to the SQLite database
db_path = 'audycje.db'
table_name = 'audycje'  # Replace with your actual table name

# Function to fetch the first row from the specified table
def fetch_first_row(db_path, table_name):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
        row = cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()
    return row

# Function to generate a longer title using KeyBERT with embeddings
def generate_long_title(content):
    # Ensure content is a string
    if not isinstance(content, str):
        content = str(content)  # Convert to string if it's not

    # Extract keywords with their scores using embeddings
    keywords = kw_model.extract_keywords(content, top_n=5, keyphrase_ngram_range=(1, 5))

    # Combine keywords to create a longer title
    title_parts = [f"{kw[0]} (Score: {kw[1]:.4f})" for kw in keywords]
    long_title = ' | '.join(title_parts)
    return long_title

# Main logic
if __name__ == "__main__":
    # Fetch the first row from the table
    first_row = fetch_first_row(db_path, table_name)

    if first_row:
        # Assuming the content is in the first column (index 0)
        content = first_row  # Adjust index based on your table structure
        print("Content:", content)

        # Generate a longer title based on the content
        long_title = generate_long_title(content)
        print("Generated Title:", long_title)
    else:
        print("No rows found in the table.")
