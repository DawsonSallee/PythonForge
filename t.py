student_records = [
    "John Doe 3.8",
    "Jane Smith 3.4",
    "Peter Jones 3.9",
    "Alice Brown 3.6",
    "Bob Davis 3.2"
]

def generate_deans_list(student_records):
    # Step 1 & 2: Split records, convert GPA to float, and filter
    deans_list_data = [record.split() for record in student_records if float(record.split()[2]) > 3.5]

    # Step 3: Format names
    formatted_names = [f"{record[1]}, {record[0]}" for record in deans_list_data]

    # Step 4: Return the list
    return formatted_names

# To test the solution with the example data:
# student_records = [...]
print(generate_deans_list(student_records))
