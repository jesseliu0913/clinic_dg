import os
import json


INPUT_FOLDER = "./output/stage1"
COMPARE_FOLDER = "./input/full_report"
input_files = [f for f in os.listdir(INPUT_FOLDER) if not f.startswith('.')]

for input_f in input_files:
  pid = input_f.split(".")[0]
  full_content = json.load(open(os.path.join(COMPARE_FOLDER, input_f), "r"))
  print(full_content['abs'])
  break


