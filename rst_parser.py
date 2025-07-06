

import os
import glob
import json

def parse_rst_file(file_path):
    """
    Parses a single .rst file according to the Simplified Blueprint.
    """
    header_char_map = {}
    current_hierarchy = []
    text_buffer = []
    output_list = []
    next_header_level = 1

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        # Rule 1: Header Detection
        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            if len(next_line) >= len(stripped_line) and len(set(next_line)) == 1 and next_line[0] in '!”#$%&\'()*+,-./:;<=>?@[\]^_`{|}~':
                header_char = next_line[0]
                if header_char not in header_char_map:
                    header_char_map[header_char] = next_header_level
                    next_header_level += 1
                level = header_char_map[header_char]

                # Rule 2: Hierarchy Management
                text_buffer.clear()
                current_hierarchy = current_hierarchy[:level-1]
                current_hierarchy.append(stripped_line)
                continue # Move to the next line

        # Rule 3: Concept & Code Pairing
        if stripped_line == '.. code-block:: python':
            code_lines = []
            # Determine indentation of the directive
            directive_indent = len(line) - len(line.lstrip(' '))
            
            # Capture indented code block
            for j in range(i + 1, len(lines)):
                code_line = lines[j]
                code_line_stripped = code_line.strip()
                
                if not code_line_stripped: # preserve blank lines within code
                    code_lines.append('')
                    continue

                code_indent = len(code_line) - len(code_line.lstrip(' '))

                if code_indent > directive_indent:
                    code_lines.append(code_line.strip())
                else:
                    break # End of code block
            
            code = "\n".join(code_lines)

            output_dict = {
                'hierarchy': list(current_hierarchy),
                'concept': " ".join(text_buffer).strip(),
                'code': code
            }
            output_list.append(output_dict)
            text_buffer.clear()
            continue

        # Rule 4: Edge Case Handling & Text Buffering
        if stripped_line and not (len(set(stripped_line)) == 1 and stripped_line[0] in '!”#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'):
             # Ignore directives that are not '.. code-block:: python'
            if stripped_line.startswith('..'):
                 continue
            text_buffer.append(stripped_line)

    return output_list

def main():
    """
    Main function to parse all .rst files in the tutorial directory.
    """
    tutorial_dir = os.path.join(os.path.dirname(__file__), 'tutorial')
    rst_files = glob.glob(os.path.join(tutorial_dir, '*.rst'))
    
    all_parsed_data = []
    for file_path in rst_files:
        all_parsed_data.extend(parse_rst_file(file_path))

    # For now, print the JSON output to stdout
    print(json.dumps(all_parsed_data, indent=2))

if __name__ == '__main__':
    main()
