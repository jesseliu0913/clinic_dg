"""
Stage 1: Using the general question to retrieve the evidence list from the provided case report
self.evidence_dict = {}
self.clean_answer_dict = {}
Stage 2: Generate the question or response for one or multiple pieces of evidence and combine them into a dialogue.
Stage 3: Order and polish the dialogue.
"""
import os
import re
import nltk
from nltk.tokenize import sent_tokenize
from DatasetTools import TextProcessingTools

nltk.download('punkt')

class MedicalDialogueProcessor:
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.pub_id = "1234"
        self.answer_folder = "./output"
        self.data = TextProcessingTools.load_json(self.data_file)
        self.clean_answer_dict = {}
        self.evidence_dict = {}
        self.dialog_dict = {}

    def generate_evidence(self):
        GENERAL_QUESTION = f"""
            Question: Describe the patient personal information.
            Question: Describe the patient experience.
            Question: Did you notice any symptoms, such as a fever, cough, or respiratory issues?
            Question: What’s imaging (only provided the figure explanation here) suggest?
            Question: What’s examination suggest? 
            Question: Is any suggestions?

            Please only output the complete sentences in the provided text that correspond to the above questions. You can list several sentences related to my query and classify which answer belongs to which query.
            Mention: Please do not miss any information in the provided text, and all of your answers should exactly match the provided text; do not change any symbols. 
            If there no information about the question just reply '$No$'
            Format should be:
            “Question: \nAnswer: \n\nQuestion: \nAnswer: ”
            I really appreciate it.
            """
        
        
        for key, article_text in self.data.items():
            user_prompt = f"{article_text}\n\n{GENERAL_QUESTION}"
            evidence = TextProcessingTools.gpt4_response(user_prompt)
            
            self.evidence_dict[key] = {
                'prompt': user_prompt,
                'answer': evidence
            }
            
        for key, value in self.evidence_dict.items():
            answer_text = value['answer'].replace('*', '')
            article_sentences = sent_tokenize(self.data[key])
            
            qa_pairs = re.findall(r'Question:(.*?)\nAnswer:(.*?)(?=\nQuestion:|\Z)', answer_text, re.DOTALL)
            
            self.clean_answer_dict[key] = {}
            for i, (question, answer) in enumerate(qa_pairs, 1):
                answer_sentences = sent_tokenize(answer.strip())
                clean_answer = [
                    token_answer if any(TextProcessingTools.is_continuous_match(token_answer, sent) 
                                      for sent in article_sentences)
                    else "$No$" in token_answer and token_answer or
                        TextProcessingTools.best_match_rouge(token_answer, article_sentences)[0]
                    for token_answer in answer_sentences
                ]
                
                self.clean_answer_dict[key][i] = {
                    'question': question,
                    'answer': answer,
                    'cleaned_answer': clean_answer
                }


        folder_path = os.path.join(self.answer_folder, "stage1")
        os.makedirs(folder_path, exist_ok=True)

        TextProcessingTools.save_json(f'{folder_path}/{self.pub_id}.json', self.clean_answer_dict)

    def generate_dialogue(self):
        clean_answer_dict = TextProcessingTools.load_json(f'{os.path.join(self.answer_folder, "stage1")}/{self.pub_id}.json')
        for key, qa_pairs in clean_answer_dict.items():
            self.dialog_dict[key] = {
                'prefix': TextProcessingTools.generate_prefix(qa_pairs),
                'patient_experience': TextProcessingTools.generate_patient_experience(qa_pairs),
                'patient_symptoms': TextProcessingTools.generate_patient_symptoms(qa_pairs),
                'image': TextProcessingTools.generate_image_analysis(qa_pairs),
                'examination': TextProcessingTools.generate_examination(qa_pairs),
                'suggestion': TextProcessingTools.generate_suggestions(qa_pairs)
            }
        
        folder_path = os.path.join(self.answer_folder, "stage2")
        os.makedirs(folder_path, exist_ok=True)

        TextProcessingTools.save_json(f'{folder_path}/{self.pub_id}.json', self.dialog_dict)
    
    def get_evidence_lst(self):
        disorder_dialog = TextProcessingTools.load_json(f'{os.path.join(self.answer_folder, "stage2")}/{self.pub_id}.json')
        qa_pairs = TextProcessingTools.load_json(f'{os.path.join(self.answer_folder, "stage1")}/{self.pub_id}.json')

        for key in list(disorder_dialog.keys()):
            evidence_lst = []
            if "evidence_list" not in list(disorder_dialog[key].keys()):
              for idx, info in enumerate(list(disorder_dialog[key].keys())):
                  reference_sentences = qa_pairs[key][str(idx + 1)]['cleaned_answer']
                  if info in ["patient_experience", "patient_symptoms"]:
                      patient_lst = []
                      dialogue = disorder_dialog[key][info]
                      patient_responses = re.findall(r"\[(.*?)\]", dialogue)
                      for idx, pr in enumerate(patient_responses):
                          best_sentence, _ = TextProcessingTools.best_match_rouge(pr, reference_sentences)
                          patient_lst.append(best_sentence)
                      evidence_lst.append(patient_lst)

                  elif info in ["image", "examination"]:
                      doctor_lst = []
                      dialogue = disorder_dialog[key][info]
                      doctor_analysis = re.findall(r"\[(.*?)\]", dialogue)
                      for idx, da in enumerate(doctor_analysis):
                          best_sentence, _ = TextProcessingTools.best_match_rouge(da, reference_sentences)
                          doctor_lst.append(best_sentence)
                      evidence_lst.append(doctor_lst)
                      
                  else:
                      continue

                  disorder_dialog[key]['evidence_list'] = evidence_lst


        folder_path = os.path.join(self.answer_folder, "stage2")
        TextProcessingTools.save_json(f'{folder_path}/{self.pub_id}.json', disorder_dialog)

    def reload_dialogue(self):
        FINAL_POLISH = """
        Enhance the clarity and readability of my text by correcting grammatical errors and improving sentence structure. Do not add any new information or change the original meaning. When the dialogue feels unnatural, try to adjust the sentences outside of the brackets first before altering the sentences within them. I would prefer if the patient's language is not too technical. The dialogue should feel natural and consistent with real-world conversations.
        """
        self.get_evidence_lst()
        final_dialogue_dict = {}
        raw_dialogue_dict = {}
        dialog_dict = TextProcessingTools.load_json(f'{os.path.join(self.answer_folder, "stage2")}/{self.pub_id}.json')
        for key in dialog_dict:
            case_dict = dialog_dict[key]
            dialog = ""
            for idx, info in enumerate(list(case_dict.keys())):
                if info != "evidence_list":
                    dialog += case_dict[info]
            final_dialogue_dict[key] = TextProcessingTools.gpt4_response(f"{FINAL_POLISH}\n\n{dialog}")
            raw_dialogue_dict[key] = dialog
        
        TextProcessingTools.save_json(f'./output/final/{self.pub_id}.json', final_dialogue_dict)
        TextProcessingTools.save_json(f'./output/stage3/{self.pub_id}.json', raw_dialogue_dict)
    
    def eval_dialogue(self):
        from rouge_score import rouge_scorer
        import sacrebleu
        from bert_score import score as bert_score
        
        raw_dialogue = TextProcessingTools.load_json(f'{os.path.join(self.answer_folder, "stage3")}/{self.pub_id}.json')
        final_dialogue = TextProcessingTools.load_json(f'{os.path.join(self.answer_folder, "final")}/{self.pub_id}.json')

        for key, raw_diag in raw_dialogue.items():
          final_diag = final_dialogue[key]
          scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
          rouge_scores = scorer.score(raw_diag, final_diag)
          bleu_score = sacrebleu.corpus_bleu([final_diag], [[raw_diag]])
          P, R, F1 = bert_score([final_diag], [raw_diag], lang='en')

          print("ROUGE Scores:", rouge_scores)
          print("BLEU Score:", bleu_score.score)
          print("BERTScore - Precision:", P.mean().item(), "Recall:", R.mean().item(), "F1:", F1.mean().item())



processor = MedicalDialogueProcessor(
  "./input/case_report/test_optical.json"
  )
processor.generate_evidence()
processor.generate_dialogue()
processor.reload_dialogue()
# processor.eval_dialogue()
