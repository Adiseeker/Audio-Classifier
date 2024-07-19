import csv

# File paths
csv_file_path = 'output.csv'
sql_file_path = 'output.sql'
table_name = 'audycje'

# Read the CSV file and extract the header and rows
with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)
    header = next(csv_reader)
    rows = list(csv_reader)

# Generate the SQL CREATE TABLE statement
columns = ', '.join([f'{col} TEXT' for col in header])  # Assuming all columns as TEXT for simplicity
create_table_stmt = f'CREATE TABLE {table_name} ({columns});'

# Generate the SQL INSERT statements
insert_stmts = []
for row in rows:
    values = ', '.join([f"'{val}'" for val in row])
    insert_stmt = f'INSERT INTO {table_name} ({", ".join(header)}) VALUES ({values});'
    insert_stmts.append(insert_stmt)

# Write the SQL statements to a file
with open(sql_file_path, 'w', encoding='utf-8') as sql_file:
    sql_file.write(create_table_stmt + '\n')
    for stmt in insert_stmts:
        sql_file.write(stmt + '\n')

print(f'SQL file generated: {sql_file_path}')
