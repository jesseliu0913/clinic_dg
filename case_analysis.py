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
from DatasetTools import TextProcessingTools


INPUT_FOLDER = "./output/stage1_output"
OUTPUT_FOLDER = "./output/stage1_parse"
input_files = [f for f in os.listdir(INPUT_FOLDER) if not f.startswith('.')]
dealed_files = [f for f in os.listdir(OUTPUT_FOLDER) if not f.startswith('.')]
intersec_files = list(set(input_files) - set(dealed_files))

confirm_lst = ['patient personal information', 'patient experience', 'any symptoms', 'the diagnosis', 'direct evidence', 'imaging', 'examination suggest', 'suggestion']
def case_check(case_content):
    qa_lst = list(case_content.keys())
    flag = 0
    for idx, qa in enumerate(qa_lst):
      groundtruth_question = confirm_lst[idx]
      question = "".join(case_content[qa]['question']).strip()
      if confirm_lst[idx] in question:
        flag += 1
      
    if flag == len(confirm_lst):
      return True
    else:
      return False

def get_combiend_sentence(combined_sentences, case, diagnoise_flag, diagnoise_sentence):
    for q_key, q_value in case.items():
      if q_key not in ['7', '3']:
        for idx, sentence in zip(q_value['cleaned_answer_idx'], q_value['cleaned_answer']):
          if idx != None:
            if idx != "$$" and idx < diagnoise_flag and sentence is not None:
              if diagnoise_sentence in sentence:
                sentence = sentence.replace(diagnoise_sentence, "<?>")
                combined_sentences.append((idx, sentence))
              else:
                combined_sentences.append((idx, sentence))
    return combined_sentences
      
def generate_oneround(oneround_dict, combined_sentences, diagnoise_response):
    combined_sentences = list(dict.fromkeys(combined_sentences))
    combined_sentences.sort(key=lambda x: x[0])
    combined_question = " ".join([sentence for _, sentence in combined_sentences])
    oneround_dict['input'] = combined_question
    oneround_dict['groundtruth'] = diagnoise_response
    oneround_dict['evidence'] = case['4']['cleaned_answer']
    return oneround_dict

def get_sentence1(multi_round_sentence1, case, diagnoise_flag, diagnoise_sentence):
    for q_key, q_value in case.items():
        if q_key in ['0', '1', '2']:
          for idx, sentence in zip(q_value['cleaned_answer_idx'], q_value['cleaned_answer']):
            if idx != None:
              if idx != "$$" and idx < diagnoise_flag and sentence is not None:
                if diagnoise_sentence in sentence:
                  sentence = sentence.replace(diagnoise_sentence, "<?>")
                  multi_round_sentence1.append((idx, sentence))
                else:
                  multi_round_sentence1.append((idx, sentence))
    return multi_round_sentence1

def get_sentence2(multi_round_sentence2, case, diagnoise_flag, diagnoise_sentence):
    for q_key, q_value in case.items():
        if q_key in ['5', '6', '4']:
          for idx, sentence in zip(q_value['cleaned_answer_idx'], q_value['cleaned_answer']):
            if idx != None:
              if idx != "$$" and idx < diagnoise_flag and sentence is not None:
                if diagnoise_sentence in sentence:
                  sentence = sentence.replace(diagnoise_sentence, "<?>")
                  multi_round_sentence2.append((idx, sentence))
                else:
                  multi_round_sentence2.append((idx, sentence))
    return multi_round_sentence2

def generate_multiround(case, multiround_dict, diagnoise_response, diagnoise_flag, diagnoise_sentence):
    multi_round_sentence1 = []
    multi_round_sentence1 = get_sentence1(multi_round_sentence1, case, diagnoise_flag, diagnoise_sentence)
    multi_round_sentence1 = list(dict.fromkeys(multi_round_sentence1))
    multi_round_sentence1.sort(key=lambda x: x[0])
    multi_round_question1 = " ".join([sentence for _, sentence in multi_round_sentence1]).replace("$No$", "")

    multi_round_sentence2 = []
    multi_round_sentence2 = get_sentence2(multi_round_sentence2, case, diagnoise_flag, diagnoise_sentence)
    multi_round_sentence2 = list(dict.fromkeys(multi_round_sentence2))
    multi_round_sentence2.sort(key=lambda x: x[0])
    multi_round_question2 = " ".join([sentence for _, sentence in multi_round_sentence2]).replace("$No$", "")
    
    if multi_round_sentence2 == []:
        multiround_dict['question'] = f"I am {multi_round_question1}. Could you consider all possible diseases based on my information? And then narrow down to a specific disease based on the examination? Only give me the disease name, and if there are different names for the same disease, list them separated by commas."
        multiround_dict['groundtruth'] = diagnoise_response
        multiround_dict['evidence'] = case['3']['cleaned_answer']
    elif multi_round_sentence1 == []:
        multiround_dict['question'] = f"I have done some examination. {multi_round_question2}. Could you consider all possible diseases based on my information? And then narrow down to a specific disease based on the examination? Only give me the disease name, and if there are different names for the same disease, list them separated by commas."
        multiround_dict['groundtruth'] = diagnoise_response
        multiround_dict['evidence'] = case['3']['cleaned_answer']
    else:
        multiround_dict['question1'] = f"I am {multi_round_question1}. Could you consider all possible diseases based on my information?"
        multiround_dict['question2'] = f"I also have done some examination,{multi_round_question2}. Could you narrow down to a specific disease based on the examination? Only give me the disease name, and if there are different names for the same disease, list them separated by commas."
        multiround_dict['groundtruth'] = diagnoise_response
        multiround_dict['evidence'] = case['3']['cleaned_answer']
    
    return multiround_dict

def with_diagnose(case):
  return case['3']['cleaned_answer_idx'] not in (['$$'], [], [0], [1], [None])

def get_cleaned_indices(cleaned_answer_idx):
    filtered = [(item, idx) for idx, item in enumerate(cleaned_answer_idx) if item is not None]
    if not filtered:  
        return False, False
    clean_idx, kept_indices = map(list, zip(*filtered))
    return clean_idx, kept_indices

def get_cleaned_case(case):
    case3_clean_idx, case3_kept_indices = get_cleaned_indices(case['3']['cleaned_answer_idx'])
    case4_clean_idx, case4_kept_indices = get_cleaned_indices(case['4']['cleaned_answer_idx'])

    if case3_clean_idx != False:
      case3_clean_idx = list(case3_clean_idx)
      case3_kept_indices = list(case3_kept_indices)
      cleaned_answer_3 = [case['3']['cleaned_answer'][i] for i in case3_kept_indices]
    else:
      cleaned_answer_3 = False
    
    if case4_clean_idx != False:
      case4_clean_idx = list(case4_clean_idx)
      case4_kept_indices = list(case4_kept_indices)
      cleaned_answer_4 = [case['4']['cleaned_answer'][i] for i in case4_kept_indices]
    else:
      cleaned_answer_4 = False

    return case3_clean_idx, case4_clean_idx, cleaned_answer_3, cleaned_answer_4


def get_diagnose_flag(case):
    case3_clean, case4_clean, cleaned_answer_3, cleaned_answer_4 = get_cleaned_case(case)

    if case3_clean != False:
        diagnose_flag = case3_clean[0]
    elif case4_clean != False and case4_clean != ['$$']:
        diagnose_flag = case4_clean[0]
    else:
        diagnose_flag = case3_clean[0]
    return diagnose_flag



for input_f in intersec_files:
    pid = input_f.split(".")[0]
    print(pid)
    if pid != "8423496":
      add_dict = {}
      file_content = json.load(open(os.path.join(INPUT_FOLDER, input_f), "r"))
      for case_key, case in file_content.items():
        if case != {}:
          if case_check(case) and with_diagnose(case) and get_cleaned_case(case) != False:
              diagnose_flag = get_diagnose_flag(case)
              add_dict[case_key] = case
              oneround_dict = {}
              multiround_dict = {}
              diagnose_lst = [ds for ds in case['3']['cleaned_answer'] if ds != None]
              diagnoise_sentence = " ".join(diagnose_lst)
              # print(diagnoise_sentence)
              sym2dia_prompt = f"Extract only the diagnosis noun(s) from the following sentence:{diagnoise_sentence}"
              diagnoise_response = TextProcessingTools.gpt4_response(sym2dia_prompt)
              # diagnoise_response = "11111"
              
              combined_sentences = []
              combined_sentences = get_combiend_sentence(combined_sentences, case, diagnose_flag, diagnoise_sentence)
              oneround_dict = generate_oneround(oneround_dict, combined_sentences, diagnoise_response)
              multiround_dict = generate_multiround(case, multiround_dict, diagnoise_response, diagnose_flag, diagnoise_sentence)
              
              add_dict[case_key]['oneround_dict'] = oneround_dict
              add_dict[case_key]['multiround_dict'] = multiround_dict
          
          # print(add_dict)
          else:
            # print(pid, case_check(case), with_diagnose())
            unqualified_dict = {pid: {"case key": case_key, "case_check": case_check(case), "with_diagnose": with_diagnose(case)}}
            with open("./output/stage1/unqualified_sparse.jsonl", 'a+') as json_file:
                json_file.write(json.dumps(unqualified_dict) + '\n')

          with open(os.path.join(OUTPUT_FOLDER, input_f), 'w') as json_file:
              json.dump(add_dict, json_file, indent=4)
      
        else:
          print("Case is empty")


# import pprint
# pprint.pprint(add_dict)



            

