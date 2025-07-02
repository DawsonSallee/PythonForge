# parser.py (Version 5.0 - The Phoenix Parser)
# This version refactors the logic for cleaner, more structured JSON output.

import os
import re
from bs4 import BeautifulSoup, NavigableString
from typing import List, Dict, Any

def get_clean_code_from_div(code_div) -> str:
    """
    Extracts PURE Python code from a highlight div by intelligently parsing
    the <span> tags and NavigableString nodes, removing all prompts and output.
    """
    pre_tag = code_div.find('pre')
    if not pre_tag:
        return ""

    code_parts = []
    for element in pre_tag.contents:
        if isinstance(element, NavigableString):
            code_parts.append(str(element))
        elif element.name == 'span':
            if 'go' in element.get('class', []) or 'gp' in element.get('class', []):
                continue
            code_parts.append(element.get_text())
            
    return "".join(code_parts).strip()

def get_section_metadata(section_tag, file_name: str, chapter_title: str) -> Dict[str, Any]:
    """Extracts and cleans metadata from a section tag."""
    header = section_tag.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if not header:
        return {}

    section_number_tag = header.find('span', class_='section-number')
    section_number = section_number_tag.text.strip() if section_number_tag else ''
    
    temp_header = BeautifulSoup(str(header), 'html.parser').find(header.name)
    if temp_header.find('span', class_='section-number'):
        temp_header.find('span', class_='section-number').decompose()
    
    section_title = temp_header.text.strip().replace('¶', '')
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
            concept_text = re.sub(r'\s+', ' ', concept_text)
            concept_text = re.sub(r'\[\d+\]', '', concept_text).strip()

            if concept_text or code_text:
                pairs.append({"concept": concept_text, "example": code_text})
            text_buffer = []
        else:
            text = element.get_text(strip=True, separator=' ').replace('¶', '').strip()
            if text:
                text_buffer.append(text)

    if text_buffer:
        concept_text = " ".join(text_buffer).strip()
        concept_text = re.sub(r'\s+', ' ', concept_text)
        concept_text = re.sub(r'\[\d+\]', '', concept_text).strip()
        if concept_text:
            pairs.append({"concept": concept_text, "example": ""})

    if pairs:
        results.append({
            "metadata": metadata,
            "pairs": pairs
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
    
    chapter_title = chapter_title_tag.text.strip() if chapter_title_tag else "Unknown Chapter"
    chapter_title = re.sub(r'\s+', ' ', chapter_title.replace('¶', '')).strip()

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