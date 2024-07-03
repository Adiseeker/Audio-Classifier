import re

# Load the HTML content from the file
with open("output.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# Split the content by the '[00:00:00.000' timestamp
blocks = re.split(r'(?=\[00:00:00\.000)', html_content)

# Ensure the first block is included correctly (it might contain important preamble information)
if not blocks[0].strip().startswith('[00:00:00.000'):
    blocks = blocks[1:]  # Remove the first block if it's not starting with timestamp

# Read the list of filenames from lista.txt and remove existing extensions
file_names = []
with open("lista.txt", "r") as list_file:
    file_names = list_file.read().splitlines()

# Remove existing extensions from filenames
file_names = [re.sub(r'\.\w+$', '', filename) for filename in file_names]

# Modify the filenames to have HTML extension
file_names = [filename + ".html" for filename in file_names]

# Write each block to a separate HTML file using the filenames from lista.txt
for i, (block, filename) in enumerate(zip(blocks, file_names)):
    with open(filename, "w", encoding="utf-8") as new_file:
        new_file.write(block)

# Print the list of created file names
print("Files written successfully:", file_names)
