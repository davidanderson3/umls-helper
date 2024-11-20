import re
import os
import argparse

def parse_mysql_script(script_path):
    """
    Parse the MySQL script to extract table names and column headers.
    Returns a dictionary with table names as keys and lists of column names as values.
    """
    table_definitions = {}
    with open(script_path, 'r') as file:
        content = file.read()

    # Regex to extract table definitions
    table_pattern = re.compile(r"CREATE TABLE (\w+) \((.*?)\) CHARACTER SET", re.DOTALL)
    column_pattern = re.compile(r"(\w+)\s+(?:char|varchar|int|text|numeric|float|double|bigint)", re.IGNORECASE)

    for table_match in table_pattern.finditer(content):
        table_name = table_match.group(1)
        columns_block = table_match.group(2)

        # Extract column names
        columns = column_pattern.findall(columns_block)
        table_definitions[table_name] = columns

    return table_definitions

def add_headers_to_rrf_files(table_definitions, rrf_dir, output_dir):
    """
    Add headers to the RRF files based on the extracted table definitions.
    Check both the main directory and the 'CHANGE' subdirectory for files.
    Ensure the header ends with a pipe if the rows have an extra pipe.
    """
    for table_name, sql_columns in table_definitions.items():
        rrf_file_main = os.path.join(rrf_dir, f"{table_name}.RRF")
        rrf_file_change = os.path.join(rrf_dir, "CHANGE", f"{table_name}.RRF")
        output_file = os.path.join(output_dir, f"{table_name}.RRF")

        if os.path.exists(rrf_file_main):
            rrf_file = rrf_file_main
        elif os.path.exists(rrf_file_change):
            rrf_file = rrf_file_change
        else:
            print(f"Warning: File {table_name}.RRF not found in main or CHANGE directory.")
            continue

        with open(rrf_file, 'r') as infile, open(output_file, 'w') as outfile:
            # Read the first line to determine the actual column count
            first_line = infile.readline().strip()
            actual_column_count = len(first_line.split('|'))

            # Write column headers as the first line, ending with a pipe
            header = "|".join(sql_columns) + "|"
            outfile.write(header + "\n")

            # Copy the rest of the file
            outfile.write(first_line + "\n")
            for line in infile:
                outfile.write(line)

        print(f"Updated {rrf_file} with headers.")

def main():
    parser = argparse.ArgumentParser(description="Add column headers to UMLS RRF files based on a MySQL script.")
    parser.add_argument("--sql", required=False, default="mysql_tables.sql", help="Path to the MySQL script file. Default is 'mysql_tables.sql' in the current directory.")
    parser.add_argument("--rrf", required=False, default=".", help="Path to the directory containing RRF files. Default is the current directory.")
    parser.add_argument("--output", required=True, help="Path to the directory for output files with headers.")
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # Parse the MySQL script
    table_definitions = parse_mysql_script(args.sql)

    # Add headers to RRF files
    add_headers_to_rrf_files(table_definitions, args.rrf, args.output)

    print("Header addition complete.")

if __name__ == "__main__":
    main()
