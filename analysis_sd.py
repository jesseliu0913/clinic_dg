"""
0: Describe the patient personal information.
1: Describe the patient experience.
2: Did you notice any symptoms, such as a fever, cough, or respiratory issues?
3: What's the diagnosis?
4: What's the direct evidence that points to this diagnosis?
5: What’s the imaging (only provided the figure explanation here) suggest?
6: What’s the examination suggest?
7: Is there any suggestion?
"""
import os
import json


FOLDER_PTAH = "./output/stage1/"
init_files = os.listdir(FOLDER_PTAH)

for int_f in init_files:
  file_content = json.load(open(os.path.join(FOLDER_PTAH, int_f), "r"))
  if file_content != {}:
      for case_key, case_content in file_content.items():
          print(case_content.keys())
      break