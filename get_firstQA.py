import os,re
import nltk
import json
from nltk.tokenize import sent_tokenize
from DatasetTools import TextProcessingTools
from DatasetGenerator import MedicalDialogueProcessor


INPUT_FOLDER = "./output/stage1"
OUTPUT_FOLDER = "./output/stage1_output"
GROUNDTRUTH_FOLDER = "./input/full_report"

input_files = [f for f in os.listdir(INPUT_FOLDER) if not f.startswith(".")]
groundtruth_files = [f for f in os.listdir(GROUNDTRUTH_FOLDER) if not f.startswith(".")]
output_files = [f for f in os.listdir(OUTPUT_FOLDER) if not f.startswith(".")]

def remove_prefix(text):
    cleaned_text = re.sub(r'^.*?(?=Question)', '', text, flags=re.DOTALL)
    return cleaned_text


def extract_values(data):
    values = []
    
    def recursive_extract(d):
        if isinstance(d, dict):
            for key, value in d.items():
                recursive_extract(value)
        elif isinstance(d, list):
            for item in d:
                recursive_extract(item)
        else:
            values.append(d)
    
    recursive_extract(data)
    return " ".join(values)

for input_f in input_files:
    if input_f not in output_files:
    # if input_f == "6298625.json":
        print(input_f)
        re_pid = []
        file_dict = {}
        file_content = json.load(open(os.path.join(INPUT_FOLDER, input_f), "r"))
        article = json.load(open(os.path.join(GROUNDTRUTH_FOLDER, input_f), "r"))

        pid = input_f.split(".")[0]

        for case_key, case_content in file_content.items():
          # print(case_content)
          file_dict[case_key] = {}
          article_keys = list(article.keys())
          if case_key in article_keys:
            article_text = " ".join([extract_values(at) if isinstance(at, dict) else at for at in article[case_key].values()])
            article_sentences = sent_tokenize(article_text)
            qa_pairs = case_content.strip().split("\n\n")
            # print(qa_pairs)
            # print(len(qa_pairs))

            # if len(qa_pairs) != 8:
              # qa_pairs = qa_pairs[1:]

            if len(qa_pairs) == 8:
              for idx, qa_pair in enumerate(qa_pairs):
                file_dict[case_key][idx] = {}
                qa_pair_split = qa_pair.split('\n')
                question = qa_pair_split[0].split(":")[1:]
                print(qa_pair_split)
                answer = "".join(qa_pair_split[1].split(":")[1:]).split(".")
                answers = [ans for ans in answer if ans != ""]

                cleaned_answer = []
                cleaned_answer_idx = []
                for idx_ans, pr in enumerate(answers):
                  if pr.lower().strip() not in ['$no$', '$no$”']:
                    best_sentence, best_idx = TextProcessingTools.best_match_rouge(pr, article_sentences)
                    cleaned_answer.append(best_sentence)
                    cleaned_answer_idx.append(best_idx)
                  else:
                    cleaned_answer.append("$NO$")
                    cleaned_answer_idx.append("$$")
                
                file_dict[case_key][idx]['question'] = question
                file_dict[case_key][idx]['answer'] = answer
                file_dict[case_key][idx]['cleaned_answer'] = cleaned_answer
                file_dict[case_key][idx]['cleaned_answer_idx'] = cleaned_answer_idx
            
            else:
                print(len(qa_pairs))
                print(pid)
      
        TextProcessingTools.save_json(f'{OUTPUT_FOLDER}/{pid}.json', file_dict)

      # else:
          # processor = MedicalDialogueProcessor(
          # f"./input/full_report/{input_f}", pid
          # )
          # processor.generate_evidence()
          # re_pid.append(pid)

# print(re_pid)

