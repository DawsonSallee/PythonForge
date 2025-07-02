# run_parser.py
# This script orchestrates the entire parsing pipeline. It finds all HTML
# files, runs the parser on them, and saves the final output to a JSON file.

import os
import json
import argparse
from parser import extract_structured_data_from_file # Import our new brilliant function

# Define the default directory where our source HTML files are stored
DEFAULT_SOURCE_DIR = "source_html"
# Define the name of the output file
OUTPUT_FILE = "extracted_data_structured.json"

def main():
    """
    Main function to run the parsing pipeline.
    """
    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Parse HTML files to extract structured concept-example data.')
    parser.add_argument('--source_dir', type=str, default=DEFAULT_SOURCE_DIR,
                        help=f'The directory containing HTML files to parse (default: {DEFAULT_SOURCE_DIR})')
    args = parser.parse_args()

    source_dir = args.source_dir
    all_documents = []

    # Create the source directory if it doesn't exist
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
        print(f"Created source directory: {source_dir}")
    
    # Check if the source directory exists
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' not found.")
        return

    # Get a list of all HTML files in the source directory
    html_files = [f for f in os.listdir(source_dir) if f.endswith('.html')]
    
    if not html_files:
        print(f"No HTML files found in '{source_dir}'. Please add your files.")
        return

    print("Starting the parsing process...")
    # Loop through each file and process it
    for file_name in html_files:
        file_path = os.path.join(source_dir, file_name)
        structured_data = extract_structured_data_from_file(file_path)
        if structured_data.get('sections'): # Only add if there is content
            all_documents.append(structured_data)
    
    print(f"\nTotal documents processed: {len(all_documents)}")
    
    # Save the final, complete list of data to our JSON file
    output_data = {
        "documents": all_documents
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print(f"Success! All structured data has been saved to '{OUTPUT_FILE}'.")
    print("Next step: Manually review this file to validate data quality.")


if __name__ == "__main__":
    main()