import os
import json
# from DatasetGenerator import MedicalDialogueProcessor


INPUT_FOLDER = "./output/stage1"
COMPARE_FOLDER = "./input/full_report"
output_files = os.listdir("./output/stage1/")
output_files_lst = [output_file.split(".")[0] for output_file in output_files]
input_files = [f for f in os.listdir(COMPARE_FOLDER) if not f.startswith('.')]

for input_f in input_files:
  pid = input_f.split(".")[0]
  if pid == '8467821':
    full_report = json.load(open(os.path.join(COMPARE_FOLDER, input_f), "r"))
    print(full_report.keys())
    



