# parser.py (Version 5.0 - The Phoenix Parser)
# This version refactors the logic for cleaner, more structured JSON output.

import os
import re
from bs4 import BeautifulSoup, NavigableString
from typing import List, Dict, Any

def get_clean_code_from_div(code_div) -> str:
    """
    Extracts PURE Python code from a highlight div, removing prompts, output,
    and excessive whitespace, while preserving indentation.
    """
    pre_tag = code_div.find('pre')
    if not pre_tag:
        return ""

    code_lines = []
    lines = pre_tag.get_text().splitlines()
    
    for i, line in enumerate(lines):
        # Preserve leading whitespace for indentation, but strip trailing whitespace
        stripped_line = line.strip()
        
        if not stripped_line: # Skip empty lines
            continue
        
        # Remove REPL prompts
        if stripped_line.startswith('>>> '):
            line = line[4:]
        elif stripped_line.startswith('... '):
            line = line[4:]
        
        # Heuristic to remove output lines:
        # If a line doesn't start with a common Python keyword, identifier, or symbol,
        # AND it's not a comment, it's likely output.
        # Also, if the previous line was a prompt and this line doesn't start with a prompt,
        # it's likely output.
        python_code_start_pattern = r'^\s*(#|import|from|def|class|if|for|while|try|with|return|pass|break|continue|raise|yield|assert|del|global|nonlocal|lambda|\w+\s*=|\w+\s*\(|[\w\[\{\(])'
        
        is_output_line = False
        if not re.match(python_code_start_pattern, line.lstrip()):
            is_output_line = True
        
        # More robust check for output lines: if the previous line was a prompt and this one isn't code
        if i > 0 and (lines[i-1].strip().startswith('>>> ') or lines[i-1].strip().startswith('... ')) and not re.match(python_code_start_pattern, line.lstrip()):
            is_output_line = True

        if is_output_line:
            continue
            
        code_lines.append(line)
            
    cleaned_code = "\n".join(code_lines)
    # Collapse multiple newlines into a single newline
    cleaned_code = re.sub(r'\n\s*\n', '\n', cleaned_code)
    # Collapse multiple spaces into one, but preserve indentation at the start of lines
    cleaned_code = re.sub(r'(?<=\S)\s{2,}', ' ', cleaned_code) # Only collapse multiple spaces *within* a line
    
    return cleaned_code.strip()

def get_section_metadata(section_tag, file_name: str, chapter_title: str) -> Dict[str, Any]:
    """
    Extracts and cleans metadata from a section tag.
    Removes the paragraph symbol from the section title.
    """
    header = section_tag.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if not header:
        return {}

    section_number_tag = header.find('span', class_='section-number')
    section_number = section_number_tag.text.strip() if section_number_tag else ''
    
    temp_header = BeautifulSoup(str(header), 'html.parser').find(header.name)
    if temp_header.find('span', class_='section-number'):
        temp_header.find('span', class_='section-number').decompose()
    
    section_title = temp_header.text.strip().replace('¶', '') # Remove the paragraph symbol
    section_title = re.sub(r'\s+', ' ', section_title).strip()

    return {
        "source_file": file_name,
        "chapter_title": chapter_title,
        "section_id": section_tag.get('id', 'unknown-section'),
        "section_number": section_number,
        "section_title": section_title
    }

def process_section(section_tag, file_name: str, chapter_title: str) -> List[Dict[str, Any]]:
    """
    Processes a section and all its nested sections, returning a flat list
    of dictionaries, where each dictionary represents a section with its pairs.
    Ensures concept text does not include section title/number and handles empty pairs.
    """
    results = []
    
    # --- Process the current section ---
    metadata = get_section_metadata(section_tag, file_name, chapter_title)
    pairs = []
    text_buffer = []
    child_sections = []

    # Iterate over direct children to separate text/code from child <section> tags
    for element in section_tag.children:
        if isinstance(element, NavigableString):
            continue

        if element.name == 'section':
            child_sections.append(element)
            continue

        is_code_block = element.name == 'div' and 'highlight' in ' '.join(element.get('class', []))
        
        if is_code_block:
            code_text = get_clean_code_from_div(element)
            concept_text = " ".join(text_buffer).strip()
            
            # Remove section number and title from concept text if present
            # This needs to be done carefully to avoid removing legitimate text
            # Check if the concept text starts with the section number and title, and remove them
            if concept_text.startswith(metadata["section_number"] + " " + metadata["section_title"]):
                concept_text = concept_text[len(metadata["section_number"] + " " + metadata["section_title"]):].strip()
            elif concept_text.startswith(metadata["section_number"]):
                concept_text = concept_text[len(metadata["section_number"]):].strip()
            elif concept_text.startswith(metadata["section_title"]):
                concept_text = concept_text[len(metadata["section_title"]):].strip()

            concept_text = re.sub(r'\s+', ' ', concept_text) # Collapse multiple spaces
            concept_text = re.sub(r'\[\d+\]', '', concept_text).strip() # Remove footnote markers

            if concept_text or code_text: # Only add if either concept or code is present
                pairs.append({"concept": concept_text, "example": code_text})
            text_buffer = []
        else:
            text = element.get_text(strip=True, separator=' ').replace('¶', '').strip()
            if text:
                text_buffer.append(text)

    # If there's any remaining text in the buffer after processing all elements,
    # and it's not followed by a code block, it forms a concept with an empty example.
    # We only add it if it's not empty.
    if text_buffer:
        concept_text = " ".join(text_buffer).strip()
        
        # Remove section number and title from concept text if present
        if concept_text.startswith(metadata["section_number"] + " " + metadata["section_title"]):
            concept_text = concept_text[len(metadata["section_number"] + " " + metadata["section_title"]):].strip()
        elif concept_text.startswith(metadata["section_number"]):
            concept_text = concept_text[len(metadata["section_number"]):].strip()
        elif concept_text.startswith(metadata["section_title"]):
            concept_text = concept_text[len(metadata["section_title"]):].strip()

        concept_text = re.sub(r'\s+', ' ', concept_text) # Collapse multiple spaces
        concept_text = re.sub(r'\[\d+\]', '', concept_text).strip() # Remove footnote markers
        if concept_text: # Only add if the concept text is not empty
            pairs.append({"concept": concept_text, "example": ""})

    # Only add the section to results if it contains at least one valid pair
    if pairs:
        # Filter out pairs where both concept and example are empty
        valid_pairs = [p for p in pairs if p["concept"] and p["example"]] # Changed to AND
        if valid_pairs:
            results.append({
                "metadata": metadata,
                "pairs": valid_pairs
            })

    # --- Recursively process child sections ---
    for child in child_sections:
        results.extend(process_section(child, file_name, chapter_title))
        
    return results

def extract_structured_data_from_file(file_path: str) -> Dict[str, Any]:
    """Main function to open and parse an HTML file into a structured format."""
    print(f"Processing file: {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    main_content = soup.find('div', role='main')
    if not main_content:
        return {}
    
    file_name = os.path.basename(file_path)
    chapter_title_tag = main_content.find('h1')
    
    chapter_title = chapter_title_tag.text.strip().replace('¶', '') if chapter_title_tag else "Unknown Chapter" # Remove ¶ from chapter title
    chapter_title = re.sub(r'\s+', ' ', chapter_title).strip()

    top_level_section = main_content.find('section')
    if not top_level_section:
        return {}

    all_sections_with_pairs = process_section(top_level_section, file_name, chapter_title)
    
    total_pairs = sum(len(sec.get("pairs", [])) for sec in all_sections_with_pairs)
    print(f"Found {len(all_sections_with_pairs)} sections with a total of {total_pairs} pairs in {file_name}.")
    
    return {
        "source_file": file_name,
        "chapter_title": chapter_title,
        "sections": all_sections_with_pairs
    }