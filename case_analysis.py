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


INPUT_FOLDER = "./output/stage1"
OUTPUT_FOLDER = "./output/stage1_parse"
input_files = [f for f in os.listdir(INPUT_FOLDER) if not f.startswith('.')]

add_dict = {}
for input_f in input_files:
    file_content = json.load(open(os.path.join(INPUT_FOLDER, input_f), "r"))
    for case_key, case in file_content.items():
      if case != {} and case['4']['cleaned_answer_idx'] != ['$$'] and case['4']['cleaned_answer_idx'] not in ([0], [1]):
          add_dict[case_key] = case
          oneround_dict = {}
          multiround_dict = {}
          diagnoise_sentence = " ".join(case['4']['cleaned_answer'])
          sym2dia_prompt = f"Extract only the diagnosis noun(s) from the following sentence:{diagnoise_sentence}"
          diagnoise_response = TextProcessingTools.gpt4_response(sym2dia_prompt)
          # diagnoise_response = "11111"
          diagnoise_flag = case['4']['cleaned_answer_idx'][0]
          combined_sentences = []
          for q_key, q_value in case.items():
            if q_key not in ['8', '4']:
              for idx, sentence in zip(q_value['cleaned_answer_idx'], q_value['cleaned_answer']):
                  if idx != "$$" and idx <= diagnoise_flag and sentence is not None:
                    if case['4']['cleaned_answer'][0] in sentence:
                      sentence = sentence.replace(case['4']['cleaned_answer'][0], "<?>")
                      combined_sentences.append((idx, sentence))
                    else:
                      combined_sentences.append((idx, sentence))

          combined_sentences = list(dict.fromkeys(combined_sentences))
          combined_sentences.sort(key=lambda x: x[0])
          combined_question = " ".join([sentence for _, sentence in combined_sentences])
          oneround_dict['input'] = combined_question
          oneround_dict['groundtruth'] = diagnoise_response
          oneround_dict['evidence'] = case['4']['cleaned_answer']

          multi_round_sentence1 = []
          for q_key, q_value in case.items():
            if q_key in ['1', '2', '3']:
              for idx, sentence in zip(q_value['cleaned_answer_idx'], q_value['cleaned_answer']):
                  if idx != "$$" and idx <= diagnoise_flag and sentence is not None:
                    if case['4']['cleaned_answer'][0] in sentence:
                      sentence = sentence.replace(case['4']['cleaned_answer'][0], "<?>")
                      multi_round_sentence1.append((idx, sentence))
                    else:
                      multi_round_sentence1.append((idx, sentence))
          
          multi_round_sentence1 = list(dict.fromkeys(multi_round_sentence1))
          multi_round_sentence1.sort(key=lambda x: x[0])
          multi_round_question1 = " ".join([sentence for _, sentence in multi_round_sentence1]).replace("$No$", "")

          multi_round_sentence2 = []
          for q_key, q_value in case.items():
            if q_key in ['5', '6', '7']:
              for idx, sentence in zip(q_value['cleaned_answer_idx'], q_value['cleaned_answer']):
                  if idx != "$$" and idx <= diagnoise_flag and sentence is not None:
                    if case['4']['cleaned_answer'][0] in sentence:
                      sentence = sentence.replace(case['4']['cleaned_answer'][0], "<?>")
                      multi_round_sentence2.append((idx, sentence))
                    else:
                      multi_round_sentence2.append((idx, sentence))
          
          multi_round_sentence2 = list(dict.fromkeys(multi_round_sentence2))
          multi_round_sentence2.sort(key=lambda x: x[0])
          multi_round_question2 = " ".join([sentence for _, sentence in multi_round_sentence2]).replace("$No$", "")
          
          if multi_round_sentence2 == []:
              multiround_dict['question'] = f"I am {multi_round_question1}. Could you consider all possible diseases based on my information? And then narrow down to a specific disease based on the examination? Only give me the disease name, and if there are different names for the same disease, list them separated by commas."
              multiround_dict['groundtruth'] = diagnoise_response
              multiround_dict['evidence'] = case['4']['cleaned_answer']
          elif multi_round_sentence1 == []:
              multiround_dict['question'] = f"I have done some examination. {multi_round_question2}. Could you consider all possible diseases based on my information? And then narrow down to a specific disease based on the examination? Only give me the disease name, and if there are different names for the same disease, list them separated by commas."
              multiround_dict['groundtruth'] = diagnoise_response
              multiround_dict['evidence'] = case['4']['cleaned_answer']
          else:
              multiround_dict['question1'] = f"I am {multi_round_question1}. Could you consider all possible diseases based on my information?"
              multiround_dict['question2'] = f"I also have done some examination,{multi_round_question2}. Could you narrow down to a specific disease based on the examination? Only give me the disease name, and if there are different names for the same disease, list them separated by commas."
              multiround_dict['groundtruth'] = diagnoise_response
              multiround_dict['evidence'] = case['4']['cleaned_answer']
          
          
          add_dict[case_key]['oneround_dict'] = oneround_dict
          add_dict[case_key]['multiround_dict'] = multiround_dict


    with open(os.path.join(OUTPUT_FOLDER, input_f), 'w') as json_file:
        json.dump(add_dict, json_file, indent=4)



            

