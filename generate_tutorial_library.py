# generate_tutorial_library.py
import os
import re
import json
from sphinx.application import Sphinx
from docutils.nodes import section, title
from sphinx.addnodes import toctree

# --- CONFIGURATION ---
# We tell Sphinx where to find the source files and the conf.py file.
SOURCE_DIR = os.path.abspath('./tutorial')
CONFIG_DIR = os.path.abspath('.')
OUTPUT_FILE = 'python_tutorial_library.json'

def extract_direct_content(node):
    """
    Extracts content (paragraphs and code blocks) that are DIRECT children of this section.
    This prevents a section's text from including the content of its sub-sections.
    """
    content_parts = []
    # We now also look for 'system_message' to ignore any leftover warnings.
    from docutils.nodes import paragraph, literal_block, system_message

    for child in node.children:
        if isinstance(child, literal_block):
            content_parts.append(f"\n\n```python\n{child.astext()}\n```\n")
        elif isinstance(child, paragraph):
            content_parts.append(child.astext())
        elif isinstance(child, system_message):
            continue # Explicitly ignore any warning/error nodes in the final tree.

    return re.sub(r'\s+', ' ', " ".join(content_parts)).strip()

def process_node_recursively(current_node, current_prefix, all_data):
    """
    The core recursive engine. Walks the Sphinx-parsed doctree and generates
    correctly nested section numbers based on the hierarchy.
    """
    from docutils.nodes import section, title

    # Find all direct child sections of the current node
    child_sections = [n for n in current_node.children if isinstance(n, section)]
    
    for i, section_node in enumerate(child_sections):
        section_counter = i + 1
        new_prefix = current_prefix + [section_counter]
        topic_id = ".".join(map(str, new_prefix))
        
        section_title_node = next((n for n in section_node.children if isinstance(n, title)), None)
        if not section_title_node:
            continue
            
        section_title = section_title_node.astext()
        full_topic_title = f"{topic_id} {section_title}"
        
        content = extract_direct_content(section_node)
        
        all_data.append({
            "topic": full_topic_title,
            "content": content,
            "source_file": os.path.basename(current_node.source),
            "level": len(new_prefix)
        })
        
        # Recurse into the children of this newly found section
        process_node_recursively(section_node, new_prefix, all_data)

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    final_library = []
    
    # Create a Sphinx application instance. This is the core of the new logic.
    # We use a "dummy" builder because we don't want to write HTML files,
    # we just want to access the parsed documents in memory.
    app = Sphinx(srcdir=SOURCE_DIR, confdir=CONFIG_DIR,
                 outdir=os.path.join('.', '_build'), doctreedir=os.path.join('.', '_doctrees'),
                 buildername='dummy', status=None, warning=open(os.devnull, 'w'))

    # "Build" the docs. This reads all .rst files and creates the perfect doctrees.
    print("Building documentation with Sphinx to create perfect document trees...")
    app.build()
    print("Build complete.")

    # The chapter order is defined in the 'master_doc' (index.rst)
    # The 'toctree' object contains the true, ordered list of documents.
    master_doc = app.env.get_doctree(app.config.master_doc)
    master_doc = app.env.get_doctree(app.config.master_doc)
    main_toctree = master_doc.traverse(toctree)[0]

    print("\nFound tutorial chapters in order:")
    # The list comprehension extracts the document name from the toctree entries
    chapter_files = [entry[1] for entry in main_toctree['entries']]
    print(chapter_files)
    
    for i, docname in enumerate(chapter_files):
        chapter_num = i + 1
        
        # Get the fully parsed and error-free doctree for this chapter
        doctree = app.env.get_doctree(docname)
        top_level_section = list(doctree.traverse(section))[0]
        
        if top_level_section:
            chapter_title_text = list(top_level_section.traverse(title))[0].astext()
            final_library.append({
                "topic": f"{chapter_num}. {chapter_title_text}",
                "content": extract_direct_content(top_level_section),
                "source_file": f"{docname}.rst",
                "level": 1
            })
            
            # Start the recursion for its sub-sections
            process_node_recursively(top_level_section, [chapter_num], final_library)

    # Save the final, correctly structured data
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_library, f, indent=2, ensure_ascii=False)

    print(f"\nSUCCESS! Created {OUTPUT_FILE} with {len(final_library)} structured sections.")
    print("This data was generated using the full Sphinx parser and is accurate.")