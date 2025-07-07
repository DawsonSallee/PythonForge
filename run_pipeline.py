import json
import os
from constants import TUTORIAL_FILES, SOURCE_DATA_PATH, OUTPUT_JSON_PATH
from rst_parser import RSTParser # <-- IMPORT THE CLASS, NOT THE FUNCTION

def main():
    all_learning_units = []
    parser = RSTParser() # <-- CREATE AN INSTANCE OF THE PARSER
    print("Starting RST parsing pipeline...")
    for filename in TUTORIAL_FILES:
        filepath = os.path.join(SOURCE_DATA_PATH, filename)
        print(f"Processing {filepath}...")
        # Use the parse_file method from the object
        units_from_file = parser.parse_file(filepath) 
        all_learning_units.extend(units_from_file)
    
    print(f"Total learning units extracted: {len(all_learning_units)}")

    with open(OUTPUT_JSON_PATH, 'w') as f:
        json.dump(all_learning_units, f, indent=2)
    
    print(f"Pipeline complete. Data saved to {OUTPUT_JSON_PATH}")

if __name__ == "__main__":
    main()