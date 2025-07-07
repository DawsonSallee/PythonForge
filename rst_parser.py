import re
from constants import HIERARCHY_RULES, SOURCE_DATA_PATH, TUTORIAL_FILES
import os
import json

class RSTParser:
    """
    A robust parser for reStructuredText files from the Python tutorial,
    designed to extract "Learning Units" consisting of a concept, its
    associated code example, and its hierarchical topic.
    """
    def __init__(self):
        # A map from an underline character to its hierarchy level (e.g., '=' -> 0)
        self.header_char_levels = HIERARCHY_RULES
        self.header_chars = set(self.header_char_levels.keys())

    def _clean_code(self, code_lines):
        """Cleans a list of code lines by removing prompts and comments."""
        cleaned_lines = []
        for line in code_lines:
            # Remove prompts like >>>, ..., and $
            line = re.sub(r"^\s*(>>> |\.\.\. |\$ |\(tutorial-env\) \$ )", "", line)
            # Ignore comments
            if line.strip().startswith("#"):
                continue
            # Ignore blankline markers used in doctests
            if "<BLANKLINE>" in line:
                continue
            cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip()

    def parse_file(self, file_path):
        """
        Parses a single .rst file and returns a list of Learning Unit dictionaries.
        """
        learning_units = []
        # Initialize a list to hold the current topic hierarchy, one slot per level
        topic_hierarchy = [""] * len(self.header_char_levels) # <-- FIX #1
        concept_buffer = []

        source_filename = os.path.basename(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped_line = line.strip()

            # --- Rule 1: Header Detection ---
            if i + 1 < len(lines) and stripped_line:
                next_line = lines[i+1].strip()
                if next_line and next_line[0] in self.header_chars and all(c == next_line[0] for c in next_line):
                    if len(next_line) >= len(stripped_line):
                        header_level = self.header_char_levels[next_line[0]] # <-- FIX #2
                        header_text = stripped_line
                        
                        concept_buffer = [] 
                        
                        topic_hierarchy[header_level] = header_text
                        for j in range(header_level + 1, len(topic_hierarchy)):
                            topic_hierarchy[j] = ""
                        
                        i += 2
                        continue

            # --- Rule 2: Code Block Detection ---
            if stripped_line.startswith(".. code-block:: python") or stripped_line.endswith("::"):
                
                code_block_lines = []
                code_start_index = i + 1
                while code_start_index < len(lines) and not lines[code_start_index].strip():
                    code_start_index += 1

                if code_start_index < len(lines):
                    first_code_line = lines[code_start_index]
                    indentation = len(first_code_line) - len(first_code_line.lstrip())
                    
                    if indentation > 0:
                        j = code_start_index
                        while j < len(lines) and (not lines[j].strip() or (len(lines[j]) - len(lines[j].lstrip()) >= indentation)):
                            code_block_lines.append(lines[j][indentation:])
                            j += 1
                        
                        unit = {
                            "unit_id": f"{source_filename}-{len(learning_units)}",
                            "source_file": source_filename,
                            "topic_hierarchy": [h for h in topic_hierarchy if h],
                            "concept_text": "\n".join(concept_buffer).strip(),
                            "example_code": self._clean_code(code_block_lines)
                        }
                        learning_units.append(unit)
                        
                        concept_buffer = []
                        i = j
                        continue
            
            # --- Rule 3: Buffer Concept Text ---
            if not stripped_line.startswith(".."):
                 concept_buffer.append(stripped_line)
            
            i += 1
        
        return learning_units