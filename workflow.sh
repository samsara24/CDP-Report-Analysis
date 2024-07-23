#!/bin/bash

# Ensure to activate the Python environment if needed
# source path/to/your/venv/bin/activate

echo "Running extract_qa_pairs.py..."
python3 extract_qa_pairs.py
if [ $? -ne 0 ]; then
    echo "extract_qa_pairs.py failed!"
    exit 1
fi

echo "Running score_process.py..."
python3 score_process.py
if [ $? -ne 0 ]; then
    echo "score_process.py failed!"
    exit 1
fi

echo "Running json_to_excel.py..."
python3 json_to_excel.py
if [ $? -ne 0 ]; then
    echo "json_to_excel.py failed!"
    exit 1
fi

echo "All scripts ran successfully!"
