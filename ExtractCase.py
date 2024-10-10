import os
import json
from bs4 import BeautifulSoup


def get_case(file_content, file_id):
    case_dict = {}
    soup = BeautifulSoup(file_content, 'xml')

    for title in soup.find_all(['h1', 'title']):
        case_title = title.get_text()
        if 'case' in case_title.lower():
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

  for input_file in input_files:
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


print(untagged_ids)