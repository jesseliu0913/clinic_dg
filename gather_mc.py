import os
import re
import json


INPUT_FOLDER = "./output/stage1_mc"
DIAG_FOLDER = "./output/stage1_parse/"
OUTPUT_FOLDER = "./output/stage1_cleanmc"
input_files = [f for f in os.listdir(INPUT_FOLDER) if not f.startswith('.')]


def extract_information(text, ruled_out, comfirmed):
    pattern = r'(?P<label>Diagnosis ruled out|Reason for exclusion|Confirmed diagnosis|Reason for confirmation):\s*(?P<content>.*?)(?=(Diagnosis ruled out|Reason for exclusion|Confirmed diagnosis|Reason for confirmation|$))'
    matches = re.finditer(pattern, text, re.DOTALL)
    extracted_info = []
    for match in matches:
        label = match.group('label')
        # print(label)
        if "ruled" in label or "exclusion" in label:
          content = match.group('content').strip()
          ruled_out.append(content)
        elif "Confirmed" in label or "confirmation" in label:
          content = match.group('content').strip()
          comfirmed.append(content)
    return ruled_out, comfirmed


def get_case_dict(input_f):
    all_cases = [json.loads(line) for line in open(os.path.join(INPUT_FOLDER, input_f), "r")]
    cases_mc = []
    for case_content in all_cases:
        case_mc = {}
        ruled_out = []
        comfirmed = []
        response1 = case_content['response1']
        response2 = case_content['response2']

        ruled_out, comfirmed = extract_information(response1, ruled_out, comfirmed)
        ruled_out, comfirmed = extract_information(response2, ruled_out, comfirmed)

        case_mc['ruled_out'] = ruled_out
        case_mc['comfirmed'] = comfirmed

        cases_mc.append(case_mc)
    return cases_mc

for input_f in input_files:
    pid = input_f.split(".")[0]
    print(pid)
    cases_mc = get_case_dict(input_f)[0]
    
    patient_info = json.load(open(os.path.join(DIAG_FOLDER, f"{pid}.json"), "r"))
    print(patient_info['case presentation:']['oneround_dict'])
    # print(patient_info['case presentation:'])
    break
    # with open(os.path.join(OUTPUT_FOLDER, input_f), "a") as jsonl_file: 
    #     for item in cases_mc:
    #         jsonl_file.write(json.dumps(item) + '\n') 