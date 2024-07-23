# Project Overview

This project is designed to analyze CDP report data for various companies. The workflow involves extracting QA pairs from raw report data, scoring these pairs using an LLM, and converting the results into an Excel file.

## File Structure

- `Reports/`
  - `data/`
    - Contains raw report data for different companies.
  - `Company/`
    - Storage path for the final generated reports.
- `support_files/`
  - Contains pre-processed data files that support the code execution.
- `config.json`
  - Configuration file with important parameters for running Claude for AWS, including company names and report years.
- `extract_qa_pairs.py`
  - Script for processing raw report data and extracting QA pairs.
- `score_process.py`
  - Script for interacting with Claude, processing prompts, and generating detailed scoring criteria based on the best and worst benchmarks, ultimately returning a JSON file.
- `json_to_excel.py`
  - Script for converting the JSON file into a target format Excel file.

## Workflow

1. Place the CDP report data to be analyzed in the `Reports/data` folder. Name the files according to the company names.
2. Update the `config.json` file with necessary details.
3. Set up the environment based on the requirements.
4. Run the three Python scripts in order, or execute the provided bat/shell script for automation.

## Steps to Execute

1. **Place Report Data:**
   - Add the CDP report data in the `Reports/data` folder. Ensure the files are named after the corresponding companies.

2. **Update Config File:**
   - Modify `config.json` to include the company names and report years you intend to analyze.

3. **Set Up Environment:**
   - Follow the instructions in `requirements.txt` to set up the necessary environment and dependencies.

4. **Run Scripts:**
   - Execute the following scripts in order:
     - `extract_qa_pairs.py`
     - `score_process.py`
     - `json_to_excel.py`
   - Alternatively, you can run the provided bat/shell script to automate the process.

## Configuration File (`config.json`)

Ensure `config.json` includes the following parameters:
- Important parameters for running Claude for AWS.
- List of company names.
- Report years.

## Requirements

Refer to `requirements.txt` for the list of dependencies and environment setup instructions.

## Additional Notes

- The `support_files` folder includes essential pre-processed data files required for the scripts to run correctly.
- The final reports will be stored in the `Reports/Company` folder after processing.

Feel free to reach out if you encounter any issues or have questions about the workflow.
