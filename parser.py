# parser.py (Version 4.0 - The Golden Parser)
# This version perfectly cleans code blocks by parsing the HTML spans.

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
    # .contents gives us a list of all children, including text nodes and tags
    for element in pre_tag.contents:
        # Check if the element is a plain text node (like a newline)
        if isinstance(element, NavigableString):
            code_parts.append(str(element))
        # Check if the element is a <span> tag
        elif element.name == 'span':
            # This is the most important rule: if it's an output span, skip it.
            if 'go' in element.get('class', []):
                continue
            
            # If it's a prompt span, also skip it.
            if 'gp' in element.get('class', []):
                continue

            # If it's any other kind of span, it's part of the code.
            # We get its text content.
            code_parts.append(element.get_text())
            
    # Join all the collected parts and strip any leading/trailing whitespace
    return "".join(code_parts).strip()


    # The ideal case where spans are structured
    for line in lines:
      # Each line can contain multiple spans for syntax highlighting
      line_spans = line.find_all('span')
      line_text = ''
      for span in line_spans:
        # The key insight: ignore spans that are console output
        if 'go' not in span.get('class', []):
          line_text += span.get_text()
      clean_code.append(line_text)

    # In some cases, the above might not work if the structure is different.
    # A more robust fallback:
    if not any(clean_code) or len(clean_code) < 2 :
        all_spans = code_div.find_all('span')
        full_text_parts = []
        for span in all_spans:
            # The most important rule: Ignore the output spans.
            if 'go' in span.get('class',[]):
                continue
            
            # Remove the prompt part of the text
            text = span.get_text()
            if 'gp' in span.get('class', []):
                text = text.replace('>>> ', '').replace('... ', '')

            full_text_parts.append(text)
        return "".join(full_text_parts).strip()


    return "\n".join(clean_code).strip()


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
    section_title = temp_header.text.strip().replace('¶', '').strip()

    return {
        "source_file": file_name,
        "chapter_title": chapter_title.replace('¶', '').strip(),
        "section_id": section_tag.get('id', 'unknown-section'),
        "section_number": section_number,
        "section_title": section_title
    }

def process_section(section_tag, file_name, chapter_title) -> List[Dict[str, Any]]:
    """Processes a single <section> tag to find concept-example pairs."""
    pairs = []
    metadata = get_section_metadata(section_tag, file_name, chapter_title)
    text_buffer = []

    for element in section_tag.children:
        if isinstance(element, NavigableString):
            continue

        is_code_block = element.name == 'div' and element.get('class') and any('highlight' in c for c in element.get('class'))

        if is_code_block:
            code_text = get_clean_code_from_div(element)
            concept_text = "\n".join(text_buffer).strip()

            if concept_text and code_text:
                content = f"Concept:\n{concept_text}\n\nExample:\n{code_text}"
                pairs.append({"content": content, "metadata": metadata.copy()})
            
            text_buffer = []
        elif element.name == 'section':
            pairs.extend(process_section(element, file_name, chapter_title))
        else:
            text = re.sub(r'\[\d+\]', '', element.get_text())
            text = text.strip().replace('¶', '').strip()
            if text:
                text_buffer.append(text)
    
    if text_buffer:
        content = f"Concept:\n" + "\n".join(text_buffer).strip()
        pairs.append({"content": content, "metadata": metadata.copy()})

    return pairs

def extract_concept_pairs_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Main function to open and parse an HTML file."""
    print(f"Processing file: {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    main_content = soup.find('div', role='main')
    if not main_content:
        return []
    
    file_name = os.path.basename(file_path)
    chapter_title_tag = main_content.find('h1')
    chapter_title = chapter_title_tag.text.strip() if chapter_title_tag else "Unknown Chapter"

    top_level_section = main_content.find('section')
    if not top_level_section:
        return []

    all_pairs = process_section(top_level_section, file_name, chapter_title)
    
    print(f"Found {len(all_pairs)} total pairs/concepts in {file_name}.")
    return all_pairs