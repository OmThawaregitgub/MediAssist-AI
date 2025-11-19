# CODE TO RUN IN YOUR LOCAL PYTHON ENVIRONMENT (e.g., Jupyter/Colab)

records = abstracts # Assuming 'abstracts' holds the final list of dicts

# 1. Open the new file for writing
with open('pubmed_data.py', 'w', encoding='utf-8') as f:
    # 2. Write the variable assignment line
    f.write("RECORDS = [\n")
    
    # 3. Write each dictionary in the list
    for i, record in enumerate(records):
        # Use json.dumps to handle formatting, then strip surrounding braces/newlines
        data_str = repr(record).replace('\n', ' ') 
        f.write(f"    {data_str}")
        if i < len(records) - 1:
            f.write(",\n")
        else:
            f.write("\n")
            
    # 4. Close the list
    f.write("]\n")

print("Created pubmed_data.py in the current directory.")