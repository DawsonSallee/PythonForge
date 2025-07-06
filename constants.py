# constants.py
TUTORIAL_FILES = [
    'appetite.rst',
    'interpreter.rst',
    'introduction.rst',
    'controlflow.rst',
    'datastructures.rst',
    'modules.rst',
    'inputoutput.rst',
    'errors.rst',
    'classes.rst',
    'stdlib.rst',
    'stdlib2.rst',
    'venv.rst',
    'whatnow.rst',
    'interactive.rst',
    'floatingpoint.rst',
    'appendix.rst'
]

# This tells the script where to find the source files inside the folder you cloned
SOURCE_DATA_PATH = 'tutorial/'

# This is the name of the final output file
OUTPUT_JSON_PATH = 'learning_units.json'

# This defines the hierarchy rules for the parser
HIERARCHY_RULES = {
    '=': 0,  # Chapter
    '-': 1,  # Section
    '^': 2,  # Sub-section
    '~': 3   # Sub-sub-section
}