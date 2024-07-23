import json
import pandas as pd
import time
import re
import os
from anthropic import AnthropicBedrock

# Read configuration from JSON file
with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

COMPANY_NAME = config['COMPANY_NAME']
REPORTING_YEAR = config['REPORTING_YEAR']
aws_access_key = config['aws_access_key']
aws_secret_key = config['aws_secret_key']
aws_region = config['aws_region']
output_json_path = COMPANY_NAME + ".json"

# Initialize the AnthropicBedrock client
client = AnthropicBedrock(
    aws_access_key=aws_access_key,
    aws_secret_key=aws_secret_key,
    aws_region=aws_region,
)

# Score dictionary
score_dict = {
    0: "Non-Compliant",
    1: "Low-Compliant",
    2: "Partially Compliant",
    3: "Baseline Compliant",
    4: "Compliant",
    5: "Beyond Compliant"
}

# Function to remove specific characters from a string
def remove_characters(input_string):
    characters_to_remove = ['"', '{', '}','/','\\']
    for char in characters_to_remove:
        input_string = input_string.replace(char, '')
    return input_string

# Function to extract score from feedback
def extract_score(feedback):
    pattern = re.compile(r'\s*(\d+)/5')
    match = pattern.search(feedback)
    if match:
        return match.group(1)
    return None

# Function to extract QA sections from feedback
def extract_qa(feedback):
    feedback = remove_characters(feedback)
    
    def extract_section_by_keywords(start_keyword, end_keyword, text):
        try:
            start_index = text.index(start_keyword) + len(start_keyword)
            end_index = text.index(end_keyword, start_index)
            return text[start_index:end_index].strip()
        except ValueError:
            return None

    def extract_score_rationale(section):
        score_match = re.search(r'Score:\s*(\d+/\d+)', section)
        rationale_match = re.search(r'Rationale\s*:\s*(.*?)(?:$|[\r\n])', section, re.DOTALL)
        score = score_match.group(1) if score_match else None
        rationale = rationale_match.group(1).replace('\n', ' ').strip() if rationale_match else None
        return score, rationale

    def extract_suggestion(section):
        suggestion_match = re.search(r'Suggestion\s*:\s*(.*?)(?:$|[\r\n])', section, re.DOTALL)
        suggestion = suggestion_match.group(1).replace('\n', ' ').strip() if suggestion_match else None
        return suggestion

    tcfd_scoring_criteria = extract_section_by_keywords('TCFD Scoring Criteria:', 'TCFD Evaluation:', feedback)
    tcfd_evaluation_section = extract_section_by_keywords('TCFD Evaluation:', 'TCFD Revision Suggestions:', feedback)
    tcfd_revision_suggestions_section = extract_section_by_keywords('TCFD Revision Suggestions:', 'IFRS S2 Scoring Criteria:', feedback)
    ifrs_scoring_criteria = extract_section_by_keywords('IFRS S2 Scoring Criteria:', 'IFRS S2 Evaluation:', feedback)
    ifrs_evaluation_section = extract_section_by_keywords('IFRS S2 Evaluation:', 'IFRS S2 Revision Suggestions:', feedback)
    ifrs_revision_suggestions_section = extract_section_by_keywords('IFRS S2 Revision Suggestions:', 'Finish Response.', feedback)
    
    tcfd_score, tcfd_rationale = extract_score_rationale(tcfd_evaluation_section)
    ifrs_score, ifrs_rationale = extract_score_rationale(ifrs_evaluation_section)
    
    tcfd_suggestion = extract_suggestion(tcfd_revision_suggestions_section)
    ifrs_suggestion = extract_suggestion(ifrs_revision_suggestions_section)

    result = {
        "TCFD Scoring Criteria": tcfd_scoring_criteria,
        "TCFD Evaluation": {
            "Score": tcfd_score,
            "Rationale": tcfd_rationale
        },
        "TCFD Revision Suggestions": {
            "Suggestion": tcfd_suggestion
        },
        "IFRS S2 Scoring Criteria": ifrs_scoring_criteria,
        "IFRS S2 Evaluation": {
            "Score": ifrs_score,
            "Rationale": ifrs_rationale
        },
        "IFRS S2 Revision Suggestions": {
            "Suggestion": ifrs_suggestion
        }
    }

    return result

# Function to process the data
def process_data(questions_file_path, qa_pairs_file_path):
    # Read Excel file
    df = pd.read_excel(questions_file_path)

    # Read QA pairs from JSON file
    with open(qa_pairs_file_path, 'r', encoding='utf-8') as file:
        qa_pairs = json.load(file)

    # Process each row in the dataframe
    company = []
    for item in df.itertuples(index=False, name='Row'):
        for qa in qa_pairs:
            for key, value in qa.items():
                if item.Question in key:
                    response = value
                    break
        
        # Define the prompt for the AI model
        prompt = (
            f'''
            Input Content: 
            Question Description: {item.Question}
            Baseline Response: {item._4}
            Best Practice: {item._5}
            TCFD Disclosure Requirements: {item._2}
            IFRS S2 Disclosure Requirements: {item._6}
            Company Response:{response}
            Output Content:
            TCFD Scoring Criteria: 
            Based on the given Question Description, Baseline Response (worst case), and Best Practice (best case), provide a 0-5 points scoring criteria specific to the TCFD requirements.
            Response Format:
            TCFD Scoring Criteria: 0-5 points based on the following:
            0 - 
            1 - 
            2 - 
            3 - 
            4 - 
            5 - 
            TCFD Evaluation: 
            Evaluate the Company's response quality and depth based on the specified TCFD disclosure requirements. Please return the following in bullet point format:
                1. Determine if the response meets the specified TCFD disclosure requirements.
                2. Provide a TCFD score (0-5) based on the TCFD Scoring Criteria.
                3. If the TCFD score is under 4,provide at least three detailed reasons in the Rationale.
            Response Format:
            TCFD Evaluation:
            Score: x/5 
            Rationale: "
            1. xxx
            2. xxx
            "
            TCFD Revision Suggestions:
            Based on the TCFD score, please return the following in bullet point format:
                1. Identify deficiencies for unmet disclosure requirements.
                2. Provide revision suggestions for each deficiency.
                3. If the TCFD score is under 4, provide at least three detailed suggestions, highlighting specific actions and examples for improvement.
            Response Format:
            TCFD Revision Suggestions:
            Suggestion: "
            1. xxx
            2. xxx
            "
            IFRS S2 Scoring Criteria:
            Based on the given Question Description, Baseline Response (worst case), and Best Practice (best case), provide a 0-5 points scoring criteria specific to the IFRS S2 requirements.
            Response Format:
            IFRS S2 Scoring Criteria:0-5 points based on the following:
            0 - 
            1 - 
            2 - 
            3 - 
            4 - 
            5 - 
            IFRS S2 Evaluation:
            Based on the IFRS S2 requirements, please return the following in bullet point format:
                1. Re-evaluate the Company's response.
                2. Provide a new score (0-5) based on the IFRS S2 Scoring Criteria.
                3. If the IFRS S2 score is under 4, should provide at least three detailed reasons in the Rationale.
            Response Format:
            IFRS S2 Evaluation:
            Score: x/5 
            Rationale: "
                1. xxx
                2. xxx
            "
            IFRS S2 Revision Suggestions:
            Based on the IFRS S2 Evaluation score, please return the following in bullet point format:
                1. Deficiencies for unmet disclosure requirements.
                2. Revision suggestions for each deficiency.
                3. If the IFRS S2 score is under 4, provide at least three detailed suggestions, highlighting specific actions and examples for improvement.
            Response Format:
            IFRS S2 Revision Suggestions:
            Suggestion: "
            1. xxx
            2. xxx
            "
            '''
        )
        
        start = time.time()
        
        # Create message to send to the AI model
        message = client.messages.create(
            max_tokens=8192,
            messages=[
                {"role": "user", "content": prompt}, 
                {"role": "assistant", "content": "{"}
            ],
            model="anthropic.claude-3-5-sonnet-20240620-v1:0"
        )
        
        end = time.time()
        result = message.content[0].text
        print(result)
        result += "Finish Response."
        
        curr = dict()
        
        # INPUT
        curr["Question ID"] = item.Category
        curr["Question Description"] = item.Question
        curr["Company Name"] = COMPANY_NAME
        curr["Reporting Year"] = REPORTING_YEAR
        curr["Company Response"] = response
        
        # BASELINE
        curr["Classification"] = item.Classification
        curr["TCFD Disclosure Requirements"] = item._2
        curr["IFRS S2 Disclosure Requirements"] = item._6
        curr["Baseline Response"] = item._4
        curr["Best Practice"] = item._5
        
        # OUTPUT
        feedback = extract_qa(result)
        curr["TCFD Scoring Criteria"] = feedback["TCFD Scoring Criteria"]
        curr["TCFD Response Score"] = extract_score(feedback["TCFD Evaluation"]["Score"])
        curr["TCFD Response Level"] = score_dict[int(extract_score(feedback["TCFD Evaluation"]["Score"]))]
        curr["TCFD Response Summary"] = feedback["TCFD Evaluation"]["Rationale"]
        curr["TCFD Response Recommendation"] = feedback["TCFD Revision Suggestions"]["Suggestion"]
        
        curr["IFRS S2 Scoring Criteria"] = feedback["IFRS S2 Scoring Criteria"]
        curr["IFRS S2 Response Score"] = extract_score(feedback["IFRS S2 Evaluation"]["Score"])
        curr["IFRS S2 Response Level"] = score_dict[int(extract_score(feedback["IFRS S2 Evaluation"]["Score"]))]
        curr["IFRS S2 Response Summary"] = feedback["IFRS S2 Evaluation"]["Rationale"]
        curr["IFRS S2 Response Recommendation"] = feedback["IFRS S2 Revision Suggestions"]["Suggestion"]
        
        curr["Run Time(s)"] = end - start
        cost = str(int(message.usage.input_tokens) / 1000000 * 3 + int(message.usage.output_tokens) / 1000000 * 15)
        curr["Cost($)"] = cost
        
        company.append(curr)

    # Save the results to a JSON file
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(company, json_file, ensure_ascii=False, indent=4)

    # Remove QA_pairs
    if os.path.exists(qa_pairs_file_path):
        os.remove(qa_pairs_file_path)
        print(f"File {qa_pairs_file_path} has been deleted")
    else:
        print(f"File {qa_pairs_file_path} does not exist")


# Specify the file paths and process the data
questions_file_path = "./support_files/new_question.xlsx"
qa_pairs_file_path = "qa_pairs.json"
process_data(questions_file_path, qa_pairs_file_path)
