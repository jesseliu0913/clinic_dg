import os
import re
import json
from bs4 import BeautifulSoup


def get_case(file_content, file_id):
    case_dict = {}
    soup = BeautifulSoup(file_content, 'xml')

    for title in soup.find_all(['title']):
        case_title = title.get_text().lower()
        # if 'case' in case_title.lower():
        if re.search(r"case report", case_title, re.IGNORECASE) or re.search(r"case \d+", case_title, re.IGNORECASE):
            # print(case_title)
            paragraph = title.find_next('p')
            if paragraph:
                case_content = paragraph.get_text()
                case_dict[case_title] = case_content

    return case_dict, soup


if __name__ == "__main__":
    INPUT_FOLDER = "./input/PMC_patient_data/"
    OUTPUT_FOLDER = "./input/case_report/"
    input_files = os.listdir(INPUT_FOLDER)
    exit_files = os.listdir(OUTPUT_FOLDER)
    exit_files_id = [file_name.split(".")[0] for file_name in exit_files]
    untagged_ids = []
    count = 0

    for input_file in input_files:
        count += 1
        file_id = input_file.split(".")[0]
        if file_id not in exit_files_id:
            f_read =  open(os.path.join(INPUT_FOLDER, input_file), 'r', encoding='utf-8')
            file_content = f_read.read()

            case_dict, soup = get_case(file_content, file_id)

            if case_dict == {}:
                untagged_ids.append(file_id)
            else:
                with open(os.path.join(OUTPUT_FOLDER, f"{file_id}.json"), 'w', encoding='utf-8') as f_save:
                    json.dump(case_dict, f_save, ensure_ascii=False, indent=4)

print(count)
print(untagged_ids)