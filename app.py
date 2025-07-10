import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# --- 1. SETUP AND CONFIGURATION (No changes needed) ---
# (This part of the code remains the same: loading .env, configuring the AI model, loading the JSON data)
load_dotenv()
try:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Error configuring AI model: {e}")
    st.stop()

@st.cache_data
def load_tutorial_data():
    try:
        with open('python_tutorial_library.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Fatal Error: `python_tutorial_library.json` not found.")
        st.info("Please make sure you have successfully run the `generate_tutorial_library.py` script first.")
        return None
library_data = load_tutorial_data()
if library_data is None:
    st.stop()
topic_titles = [item['topic'] for item in library_data]


# --- 2. THE PROMPT ENGINEERING TOOLKIT (The Major New Section) ---

# We now have a dictionary of prompt templates for the different quiz modes.
# You can add more prompts here just by adding a new key-value pair.
PROMPT_TEMPLATES = {
            "Complete Section Review": """
        You are The Python Sage, an exceptionally thorough and systematic tutor.
        Your one and only task is to create a comprehensive, point-by-point review of the entire text provided. You must not leave out any concept or sub-topic.
        Your difficulty instructions are: {difficulty_instructions}

        **CONTEXT TO USE:**
        ---
        {content}
        ---

        **CRITICAL TASK & FORMATTING DIRECTIVES:**
        1.  **Iterate Systematically:** Go through the `CONTEXT TO USE` from top to bottom. For EVERY distinct concept, function, or syntax example you find, you MUST generate a corresponding review point.
        2.  **Do Not Summarize or Select:** Your goal is 100% coverage, not to pick the "most important" ideas. If the text mentions it, you must include it.
        3.  **Writing Style:** Use clear, direct language. The definition should be brief and technical.
        4.  Each review point MUST include a definition and a concise, illustrative code example.
        5.  All code examples MUST be in a Markdown code block (```python ... ```).
        6.  You MUST follow the output structure below for every single concept found.

        **MANDATORY OUTPUT STRUCTURE:**

        ### 1. [Name of the First Concept Found]
        
        **Definition:** [A clear, technical definition of the concept.]

        **Example:**
        ```python
        # A concise code example demonstrating this specific concept.
        ```

        ---

        ### 2. [Name of the Second Concept Found]

        **Definition:** [A clear, technical definition of the concept.]

        **Example:**
        ```python
        # A concise code example demonstrating this specific concept.
        ```

        ---

        ### 3. [Name of the Third Concept Found]
        
        (Continue this exact pattern, creating a new numbered section for EVERY concept in the provided text until you have covered all of them.)
    """,
    "5 Code Challenges": """
        You are The Python Sage, an author of clear and concise coding exercises.
        Your task is to generate 5 practical code challenges based ONLY on the provided text.
        Your difficulty instructions are: {difficulty_instructions}

        **CONTEXT TO USE:**
        ---
        {content}
        ---

        **CRITICAL TASK & FORMATTING DIRECTIVES:**
        1.  Generate exactly 5 distinct challenges.
        2.  **Scoping Rule: Each challenge and its solution MUST prioritize using only the concepts, functions, and syntax examples found directly in the CONTEXT TO USE. Avoid introducing more advanced topics unless absolutely necessary for a coherent problem.**
        3.  **Writing Style:** Your goal is conciseness. Use clear and direct language. Avoid unnecessary words and filler. The Task description should be as short as possible while remaining clear.
        4.  You MUST provide a clear Input and the corresponding Expected Output for each challenge.
        5.  The solution code MUST be in a Markdown code block (```python ... ```).
        6.  You MUST follow the output structure below exactly, including the blank lines for spacing.

        **MANDATORY OUTPUT STRUCTURE:**

        **1. Code Challenge: [A short title, e.g., "Filtering a List"]**

        **Task:** [A clear and direct description of the goal. Be concise.]

        **Input:**
        ```python
        numbers = [1, 2, 3, 4, 5, 6]
        ```

        **Expected Output:**
        ```text
        [2, 4, 6]
        ```

        


        **Solution:**
        ```python
        # The concise and correct code solution.
        numbers = [1, 2, 3, 4, 5, 6]
        evens = [n for n in numbers if n % 2 == 0]
        print(evens)
        ```

        ---

        **2. Code Challenge: [Another short title]**

        (Follow the exact same structure as above, including the three `<br>` tags for spacing)

        ---
        (Continue this exact pattern for all 5 challenges)
    """,
    "1 Comprehensive Code Challenge": """
        You are "The Python Sage," a master designer of intricate, multi-step coding puzzles and capstone challenges, modeling your output after professional coding platforms.
        Your primary task is to generate 1 high-quality, comprehensive coding challenge based ONLY on the provided text. This challenge must intelligently weave together multiple, distinct concepts from the context.
        Your difficulty instructions are: {difficulty_instructions}

        **CONTEXT TO USE:**
        ---
        {content}
        ---

        **CRITICAL TASK & FORMATTING DIRECTIVES:**
        1.  **Scoping Rule: The challenge and its solution MUST be solvable using only the concepts, functions, and syntax examples found directly in the CONTEXT TO USE. The goal is to weave together multiple concepts *from the provided text*, not to introduce new ones.**
        2.  You MUST create a realistic **Scenario** and a clear **Task**.
        3.  The task description MUST include an **Example Input** and the corresponding **Expected Output**.
        4.  Both the Example Input and Expected Output MUST be in Markdown code blocks.
        5.  The **Solution** section should ONLY contain the code that solves the problem and a detailed **Explanation**.
        6.  You MUST follow the output structure below with no deviations.

        **MANDATORY OUTPUT STRUCTURE:**

        **Challenge: [Create a Descriptive Title for the Challenge]**

        **Scenario:**
        [A 1-2 sentence story or context for the problem. e.g., "You are building a data processing pipeline for a university. You need to filter and format a list of student records."]

        **Your Task:**
        Write a function `process_records(records)` that takes a list of dictionaries and performs the following actions:
        - It must use a list comprehension to filter for students with a GPA over 3.5.
        - It must use the `map()` function to format the names of the selected students into "Last Name, First Name".
        - Finally, it must return a list of the formatted names.

        **Example Input:**
        ```python
        student_data = [
            {{'first_name': 'John', 'last_name': 'Doe', 'gpa': 3.8}},
            {{'first_name': 'Jane', 'last_name': 'Smith', 'gpa': 3.4}},
            {{'first_name': 'Peter', 'last_name': 'Jones', 'gpa': 3.9}},
        ]
        ```

        **Expected Output:**
        ```text
        ['Doe, John', 'Jones, Peter']
        ```

        **Hint:**
        [A single, helpful sentence. e.g., "Remember that you can chain operations, feeding the output of one step into the input of the next."]

        ---
        
        **Solution:**
        ```python
        # The complete, well-commented Python code for the solution goes here.
        def process_records(records):
            # Step 1: Filter students using a list comprehension
            honor_roll = [rec for rec in records if rec['gpa'] > 3.5]
            
            # Step 2: Format names using map and a lambda function
            formatted_names = map(lambda rec: f"{{rec['last_name']}}, {{rec['first_name']}}", honor_roll)
            
            # Step 3: Return the final list
            return list(formatted_names)

        # To test the solution with the example data:
        # student_data = [ ... ] 
        # print(process_records(student_data))
        ```

        **Explanation:**
        - **List Comprehension:** We used a list comprehension (`[rec for rec in records if rec['gpa'] > 3.5]`) to concisely filter the original list.
        - **`map()` Function:** The `map()` function was used to apply a `lambda` function to each item of the `honor_roll` list.
        - **`list()` Constructor:** We wrapped the `map` object in `list()` to convert the iterator into a concrete list for the return value.

        ---
    """,
    "5 Conceptual Questions": """
        You are "The Python Sage," an expert Python tutor who creates rich, illustrative learning materials.
        Your primary task is to generate 5 distinct learning points based ONLY on the provided text.
        Your difficulty instructions are: {difficulty_instructions}

        **CONTEXT TO USE:**
        ---
        {content}
        ---

        **CRITICAL TASK & FORMATTING DIRECTIVES:**
        1.  Generate exactly 5 learning points from the CONTEXT.
        2.  Each point MUST consist of three parts: a conceptual question, a text answer, and an illustrative code example.
        3.  The code example MUST be a short, clean, and relevant Python snippet that demonstrates the concept in the answer.
        4.  The code example MUST be formatted in a Markdown code block, like this: ```python\n# your code here\n```.
        5.  You MUST follow the output structure below with no deviations.
        6.  **Scoping Rule: Each question, answer, and code example MUST be derived directly from the concepts and examples in the CONTEXT TO USE. Do not introduce outside topics or more complex syntax.**

        **MANDATORY OUTPUT STRUCTURE:**

        **1. Concept: [Name of the Concept]**

        **Question:** 
        
        [Your first generated conceptual question text here...]

        **Answer:** 
        
        [Your concise answer text here, explaining the concept clearly.]

        **Code Example:**
        ```python
        # A short, relevant Python code snippet that illustrates the answer.
        # For example, demonstrating list comprehensions.
        squares = [x**2 for x in range(5)]
        print(f"The squares are: ...")
        ```

        ---

        **2. Concept: [Name of the Second Concept]**

        **Question:** 
        
        [Your second generated conceptual question text here...]

        **Answer:** 
        
        [Your concise answer text here.]

        **Code Example:**
        ```python
        # Another code snippet illustrating the second concept.
        ```

        ---
        (Continue this exact pattern for all 5 concepts)
    """,
    "5 Find the Flaw Challenges": """
        You are "The Python Sage," a meticulous code reviewer and debugging expert.
        Your primary task is to generate 5 distinct debugging scenarios based ONLY on the provided text.
        Your difficulty instructions are: {difficulty_instructions}

        **CONTEXT TO USE:**
        ---
        {content}
        ---

        **CRITICAL TASK & FORMATTING DIRECTIVES:**
        1.  Generate exactly 5 scenarios. Each scenario is a complete learning module with all parts visible.
        2.  For each scenario, you MUST provide the following in order: the Goal, the Buggy Code, the Flaw, and the Corrected Code.
        3.  Both the buggy code and the corrected code MUST be in their own separate Markdown code blocks (```python ... ```).
        4.  You MUST follow the output structure below with no deviations.
        5.  **Scoping Rule: The bug in each scenario MUST be related to a misunderstanding or misuse of a concept found in the CONTEXT TO USE. The corrected code should also use concepts from the text.**

        **MANDATORY OUTPUT STRUCTURE:**

        **1. Debugging Scenario: [Name of the Bug or Concept]**

        **Goal:** This code is supposed to [describe the intended outcome of the code].

        **Buggy Code:**
        ```python
        # The buggy, non-working code snippet goes here.
        # For example, a loop that has an off-by-one error.
        numbers = [1, 2, 3, 4, 5]
        for i in range(len(numbers) + 1):
            print(numbers[i])
        ```

        **The Flaw:** [A clear and concise explanation of the bug.]

        **Corrected Code:**
        ```python
        # The corrected, working code snippet goes here.
        numbers = [1, 2, 3, 4, 5]
        for i in range(len(numbers)):
            print(numbers[i])
        ```

        ---

        **2. Debugging Scenario: [Name of the Second Bug]**

        (Follow the exact same structure as above for the second scenario)

        ---
        (Continue this exact pattern for all 5 scenarios)
    """
}

# This dictionary holds the specific instructions for each difficulty level.
DIFFICULTY_LEVELS = {
    "Easy": "Assume the user is a beginner. Focus on the most fundamental concepts and examples. Keep questions and challenges straightforward and simple.",
    "Intermediate": "Assume the user understands the basics. Ask questions that require combining one or two ideas. Code challenges can be slightly more complex.",
    "Advanced": "Assume the user is comfortable with the topic. Ask nuanced questions that test deep knowledge of edge cases or interactions between concepts. Challenges can be more open-ended or complex."
}


# --- 3. THE UPGRADED USER INTERFACE ---

st.title("🐍 The Python Sage")
st.caption("Your personal Python tutor, powered by the official documentation.")

st.sidebar.header("Quiz Controls")

# UI for selecting the topic (unchanged)
selected_topic = st.sidebar.selectbox(
    "1. Choose a topic:",
    options=topic_titles,
    index=None,
    placeholder="Select a topic..."
)

# NEW: UI for selecting the Quiz Mode
selected_quiz_mode = st.sidebar.radio(
    "2. Select a quiz mode:",
    options=PROMPT_TEMPLATES.keys(), # The keys from our dictionary
    index=0 # Default to the first one, "Hybrid Quiz"
)

# NEW: UI for selecting the Difficulty
selected_difficulty = st.sidebar.select_slider(
    "3. Select a difficulty:",
    options=DIFFICULTY_LEVELS.keys(), # The keys from our dictionary
    value="Intermediate" # Default to the middle value
)

# UI for the comprehensive review checkbox (unchanged)
comprehensive_mode = st.sidebar.checkbox(
    "4. Make it a Comprehensive Review",
    help="Check this box to include all sub-sections of the selected topic in the quiz."
)

# The generate button (unchanged)
generate_button = st.sidebar.button("✨ Generate My Quiz!", type="primary", use_container_width=True)


# --- 4. THE DYNAMIC APPLICATION LOGIC ---

if generate_button and selected_topic:
    
    # Logic for gathering content based on comprehensive mode (unchanged)
    content_for_ai = ""
    quiz_title = selected_topic
    if not comprehensive_mode:
        for item in library_data:
            if item['topic'] == selected_topic:
                content_for_ai = item['content']
                break
    else:
        base_topic_number = selected_topic.split(' ')[0]
        relevant_items = [item for item in library_data if item['topic'].startswith(base_topic_number)]
        combined_content_parts = [f"### From section: {item['topic']}\n\n{item['content']}\n\n---\n" for item in relevant_items]
        content_for_ai = "\n".join(combined_content_parts)
        main_chapter_num_str = base_topic_number.split('.')[0]
        main_chapter_entry = next((item for item in library_data if item['topic'].split(' ')[0] == f"{main_chapter_num_str}."), None)
        if main_chapter_entry:
            main_title_text = main_chapter_entry['topic'].split(' ', 1)[1]
            quiz_title = f"Comprehensive Review: {main_title_text}"
        else:
            quiz_title = f"Comprehensive Review of Chapter {main_chapter_num_str}"

    # --- NEW: Dynamically build the final prompt ---
    if content_for_ai:
        # 1. Get the chosen prompt template from the dictionary
        prompt_template = PROMPT_TEMPLATES[selected_quiz_mode]

        # 2. Get the chosen difficulty instructions from the dictionary
        difficulty_instructions = DIFFICULTY_LEVELS[selected_difficulty]

        # 3. Combine them into the final prompt
        final_prompt = prompt_template.format(
            difficulty_instructions=difficulty_instructions,
            content=content_for_ai
        )
        
        # --- The rest of the logic is the same ---
        spinner_title = f"{selected_quiz_mode} ({selected_difficulty})"
        with st.spinner(f"The Sage is crafting your '{spinner_title}' for: **{quiz_title}**..."):
            try:
                response = model.generate_content(final_prompt)
                st.header(f"{selected_quiz_mode}: {quiz_title}", divider="rainbow")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred while generating the quiz: {e}")
    else:
        st.error("Could not find content for the selected topic.")

elif generate_button and not selected_topic:
    st.warning("Please select a topic from the dropdown menu first.")