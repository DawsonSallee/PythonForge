# run_parser.py
# This script orchestrates the entire parsing pipeline. It finds all HTML
# files, runs the parser on them, and saves the final output to a JSON file.

import os
import json
from parser import extract_concept_pairs_from_file # Import our brilliant function

# Define the directory where our source HTML files are stored
SOURCE_DIR = "source_html"
# Define the name of the output file
OUTPUT_FILE = "extracted_data.json"

def main():
    """
    Main function to run the parsing pipeline.
    """
    all_extracted_data = []
    
    # Get a list of all HTML files in the source directory
    html_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.html')]
    
    if not html_files:
        print(f"No HTML files found in '{SOURCE_DIR}'. Please add your files.")
        return

    print("Starting the parsing process...")
    # Loop through each file and process it
    for file_name in html_files:
        file_path = os.path.join(SOURCE_DIR, file_name)
        # The 'extend' method is perfect for adding all items from one list to another
        all_extracted_data.extend(extract_concept_pairs_from_file(file_path))
    
    print(f"\nTotal pairs extracted from all files: {len(all_extracted_data)}")
    
    # Save the final, complete list of data to our JSON file
    # We use indent=2 to make the JSON file human-readable for our validation step
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_extracted_data, f, indent=2, ensure_ascii=False)
        
    print(f"Success! All data has been saved to '{OUTPUT_FILE}'.")
    print("Next step: Manually review this file to validate data quality.")


if __name__ == "__main__":
    main()