import os
import nltk
import json
from nltk.tokenize import sent_tokenize
from DatasetTools import TextProcessingTools
from DatasetGenerator import MedicalDialogueProcessor


INPUT_FOLDER = "./output/stage1"
OUTPUT_FOLDER = "./output/stage_output"
GROUNDTRUTH_FOLDER = "./input/full_report"

input_files = [f for f in os.listdir(INPUT_FOLDER) if not f.startswith(".")]
groundtruth_files = [f for f in os.listdir(GROUNDTRUTH_FOLDER) if not f.startswith(".")]
output_files = [f for f in os.listdir(OUTPUT_FOLDER) if not f.startswith(".")]



    # processor = MedicalDialogueProcessor(
    #     f"./input/full_report/{input_file}", file_id
    #     )
    # processor.generate_evidence()
