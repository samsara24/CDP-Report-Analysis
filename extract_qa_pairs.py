import pandas as pd
import json
import re

# Read the questions file
with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

COMPANY_NAME = config['COMPANY_NAME']
questions_file_path = r"./support_files/questions_detailed_classification_corrected.xlsx"
questions_df = pd.read_excel(questions_file_path)

# Read the answers file
answers_file_path = f"./Reports/data/{COMPANY_NAME}.txt"
with open(answers_file_path, 'r', encoding="utf-8") as file:
    answers_content = file.read()

# Initialize the QA pairs list
qa_pairs = []

# Iterate through each question to find corresponding answers
for question in questions_df['Question']:
    # Find the starting index of the question in the answers content
    start_index = answers_content.find(question)
    if start_index != -1:
        # Find the ending index of the current question's answer
        end_index = len(answers_content)
        next_question_index = start_index
        for next_question in questions_df['Question']:
            next_question_index = answers_content.find(next_question, start_index + len(question))
            if next_question_index != -1:
                end_index = next_question_index
                break
        
        # Extract the answer
        answer = answers_content[start_index + len(question):end_index].strip()
        
        # Regular expression to match the question pattern
        pattern = re.compile(r'^C\d{1,2}\.\d{1,2}[a-z]?', re.MULTILINE)
        
        # Split the answer content into segments based on the pattern
        segments = pattern.split(answer)
        
        # Append the question-answer pair to the list
        qa_pairs.append({question: segments[0]})

# Write the QA pairs to a JSON file
output_json_path = "qa_pairs.json"
with open(output_json_path, 'w', encoding="utf-8") as json_file:
    json.dump(qa_pairs, json_file, ensure_ascii=False, indent=4)
