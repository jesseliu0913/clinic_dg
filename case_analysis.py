"""
Parse the Stage 1
1 Question: Describe the patient personal information.
2 Question: Describe the patient experience.
3 Question: Did you notice any symptoms, such as a fever, cough, or respiratory issues?
4 Question: What's the diagnosis?
5 Question: What's the direct evidence that points to this diagnosis?
6 Question: What’s the imaging (only provided the figure explanation here) suggest?
7 Question: What’s the examination suggest?
8 Question: Is there any suggestion?
"""
import os
import json


INPUT_FOLDER = "./output/stage1"
OUTPUT_FOLDER = "./output/stage1_parse"
input_files = [f for f in os.listdir(INPUT_FOLDER) if not f.startswith('.')]

for input_f in input_files:
    file_content = json.load(open(os.path.join(INPUT_FOLDER, input_f), "r"))
    for case_key, case in file_content.items():
      if case != {}:
        if case['4']['cleaned_answer_idx'] != ['$$']:  
            with open(f"{OUTPUT_FOLDER}/{input_f}", 'w') as json_file:
                json.dump(file_content, json_file, indent=4)
            

