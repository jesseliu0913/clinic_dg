import os
import json


INPUT_FOLDER = "./input/full_report"
input_files = [f for f in os.listdir(INPUT_FOLDER) if not f.startswith(".")]

for input_f in input_files:
  pid = input_f.split(".")[0]
  if pid == '4869430':
      file_content = json.load(open(os.path.join(INPUT_FOLDER, input_f), "r"))
      title_lst = list(file_content.keys())
      case_title = [t for t in title_lst if 'case' in t.lower() and len(t.split(" ")) <=3]
      print(title_lst)
      if case_title != []:
        for case_t in case_title:
          case_content = file_content[case_t]
          # print(case_content)
        break

    