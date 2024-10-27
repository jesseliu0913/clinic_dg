"""
Stage 1: Using the general question to retrieve the evidence list from the provided case report
self.evidence_dict = {}
self.clean_answer_dict = {}
Stage 2: Generate the question or response for one or multiple pieces of evidence and combine them into a dialogue.
Stage 3: Order and polish the dialogue.
"""
import os
import re
import spacy
import pickle
import nltk
from nltk.tokenize import sent_tokenize
from DatasetTools import TextProcessingTools


nltk.download('punkt')
nlp = spacy.load('en_core_web_sm')

class MedicalDialogueProcessor:
    def __init__(self, data_file: str, file_id: str):
        self.data_file = data_file
        self.pub_id = file_id
        self.answer_folder = "./output"
        self.data = TextProcessingTools.load_json(self.data_file)
        self.clean_answer_dict = {}
        self.evidence_dict = {}
        self.dialog_dict = {}
        self.text_process = TextProcessingTools()
        

    def generate_evidence(self):
        GENERAL_QUESTION = f"""
            Question: Describe the patient personal information.
            Question: Describe the patient experience.
            Question: Did you notice any symptoms, such as a fever, cough, or respiratory issues?
            Question: What's the diagnosis?
            Question: What's the direct evidence that points to this diagnosis?
            Question: What’s the imaging (only provided the figure explanation here) suggest?
            Question: What’s the examination suggest?
            Question: Is there any suggestion?

            Please only output the complete sentences in the provided text that correspond to the above questions. You can list several sentences related to my query and classify which answer belongs to which query.
            Mention: Please do not miss any information in the provided text, and all of your answers should exactly match the provided text; do not change any symbols. 
            If there no information about the question just reply '$No$'
            Format should be:
            “Question: \nAnswer: \n\nQuestion: \nAnswer: ”
            I really appreciate it.
            """
        
        for key, article_text in self.data.items():
            if 'case' in key.lower() and len(key.split(" ")) < 4:
                user_prompt = f"{article_text}\n\n{GENERAL_QUESTION}"
                evidence = TextProcessingTools.gpt4_response(user_prompt)
                
                self.evidence_dict[key] = {
                    'prompt': user_prompt,
                    'answer': evidence
                }

        if self.evidence_dict != {}:
            for key, value in self.evidence_dict.items():
                answer_text = value['answer'].replace('*', '')
                self.clean_answer_dict[key] = answer_text
                # article_sentences = sent_tokenize(self.data[key]['content'])
                # qa_pairs = re.findall(r'Question:(.*?)\nAnswer:(.*?)(?=\nQuestion:|\Z)', answer_text, re.DOTALL)
                '''
                self.clean_answer_dict[key] = {}
                for i, (question, answer) in enumerate(qa_pairs, 1):
                    answer_sentences = sent_tokenize(answer.strip())
                    clean_answer = []
                    clean_answer_idx = []

                    for idx, token_answer in enumerate(answer_sentences):
                        match_found = False
                        for sent_idx, sent in enumerate(article_sentences):
                            if TextProcessingTools.is_continuous_match(token_answer, sent):
                                clean_answer.append(token_answer)
                                clean_answer_idx.append(sent_idx)  
                                match_found = True
                                break
                        if not match_found:
                            if "$No$" in token_answer:
                                clean_answer.append(token_answer)
                                clean_answer_idx.append("$$")  
                            else:
                                best_match, sent_idx = TextProcessingTools.best_match_rouge(token_answer, article_sentences)
                                clean_answer.append(best_match)
                                clean_answer_idx.append(sent_idx) 

                    
                    self.clean_answer_dict[key][i] = {
                        'question': question,
                        'answer': answer,
                        'cleaned_answer': clean_answer,
                        'cleaned_answer_idx': clean_answer_idx,
                    }
                '''

            folder_path = os.path.join(self.answer_folder, "stage1")
            os.makedirs(folder_path, exist_ok=True)

            TextProcessingTools.save_json(f'{folder_path}/{self.pub_id}.json', self.clean_answer_dict)
            print(f"Success {self.pub_id}")
            return "yes"
        else:
            # print("No Case Report in this Article")
            return self.pub_id

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
    
    def _get_evidence_lst(self):
        disorder_dialog = TextProcessingTools.load_json(f'{os.path.join(self.answer_folder, "stage2")}/{self.pub_id}.json')
        qa_pairs = TextProcessingTools.load_json(f'{os.path.join(self.answer_folder, "stage1")}/{self.pub_id}.json')

        for key in list(disorder_dialog.keys()):
            evidence_lst = []
            for idx in range(len(list(disorder_dialog[key].keys())) - 1):
                info = list(disorder_dialog[key].keys())[idx]
                reference_sentences = qa_pairs[key][str(idx + 1)]['cleaned_answer']
                # evidence_lst.extend(reference_sentences)
                if info in ["patient_experience", "patient_symptoms"]:
                    patient_lst = []
                    dialogue = disorder_dialog[key][info]
                    patient_responses = re.findall(r"\[(.*?)\]", dialogue)
                    for idx, pr in enumerate(patient_responses):
                        best_sentence, _ = TextProcessingTools.best_match_rouge(pr, reference_sentences)
                        dialogue = dialogue.replace(str(pr), f"{info}_{idx}")
                        patient_lst.append(best_sentence)
                    disorder_dialog[key][info] = dialogue
                    evidence_lst.append(patient_lst)

                elif info in ["image", "examination"]:
                    doctor_lst = []
                    dialogue = disorder_dialog[key][info]
                    doctor_analysis = re.findall(r"\[(.*?)\]", dialogue)
                    for idx, da in enumerate(doctor_analysis):
                        best_sentence, _ = TextProcessingTools.best_match_rouge(da, reference_sentences)
                        dialogue = dialogue.replace(str(da), f"{info}_{idx}")
                        doctor_lst.append(best_sentence)
                    disorder_dialog[key][info] = dialogue
                    evidence_lst.append(doctor_lst)
                    
                else:
                    continue

                disorder_dialog[key]['evidence_list'] = evidence_lst


        folder_path = os.path.join(self.answer_folder, "stage2")
        TextProcessingTools.save_json(f'{folder_path}/{self.pub_id}_evident.json', disorder_dialog)
    

    def reload_dialogue(self):
        FINAL_POLISH = """
        Polish the following doctor-patient dialogue to make it sound more natural and consistent. Add conjunctions or filler words outside of the brackets to improve the flow, but ***do not change any words or symbols inside the brackets***. ***Keep the brackets as they are***. Additionally, add natural phrases before or after the bracketed content, maintaining the dialogue flow. Make sure the interaction between the patient and doctor is smooth and complete.
        """
        self._get_evidence_lst()
        polished_dialogue_dict = {}
        dialog_dict = TextProcessingTools.load_json(f'{os.path.join(self.answer_folder, "stage2")}/{self.pub_id}_evident.json')
        for key in dialog_dict:
            case_dict = dialog_dict[key]
            evidence_list = case_dict['evidence_list']
            dialog = ""
            for idx, info in enumerate(list(case_dict.keys())):
                if info != "evidence_list":
                    dialog += case_dict[info]

            polished_dialogue = TextProcessingTools.gpt4_response(f"""{FINAL_POLISH}\n\n{dialog}""")
            
            for info_index, info in enumerate(["patient_experience", "patient_symptoms", "image", "examination"]):
                for idx in range(len(evidence_list[info_index])):
                    tag_name = f"{info}_{idx}"
                    tag_info = evidence_list[info_index][idx]
                    polished_dialogue = polished_dialogue.replace(tag_name, tag_info)  # update polished_dialogue

            polished_dialogue_dict[key] = polished_dialogue

        TextProcessingTools.save_json(f'./output/stage3/{self.pub_id}.json', polished_dialogue_dict)
    
    def refine_dialogue(self):
        import ast

        refine_dialogue_dict = {}
        dialogue = TextProcessingTools.load_json(f'./output/stage3/{self.pub_id}.json')

        for case_key, case_value in dialogue.items():
            refine_dialogue_dict[case_key] = {}
            final_dialogue = ""
            lines = case_value.strip().split('\n')
            doctor_words = []
            patient_words = []
            doctor_regex = re.compile(r'^Doctor: (.*)$')
            patient_regex = re.compile(r'^Patient: (.*)$')

            for line in lines:
                doc_match = doctor_regex.match(line)
                pat_match = patient_regex.match(line)

                if doc_match:
                    words = str(doc_match.group(1))
                    evidence_lst = re.findall(r'\[(.*?)\]', words)
                    evidence_length = len(evidence_lst)
                    if evidence_length > 1:
                        CONNECT_PROMPT = f"""
                            I have the following 4 sentences in a list that I want to connect in a natural, flowing order:
                            ['The patient experienced sudden onset of shortness of breath.', 'The chest X-ray showed clear lungs.', 'She was started on bronchodilators and steroids to manage the symptoms.', 'Her condition improved significantly over the next 48 hours.']
                            Could you provide 3 conjunction words to connect these sentences naturally? 
                            The output should be in the format: [word1, word2, word3].
                            Answers: [However, Therefore, As a result]

                            I have the following {evidence_length} sentences in a list that I want to connect in a natural, flowing order:
                            {evidence_lst}
                            Could you provide {evidence_length - 1} conjunction words to connect these sentences naturally? 
                            The output should be in the format: [word1, word2, word3].
                            Answers:
                            """
                        answers = TextProcessingTools.gpt4_response(CONNECT_PROMPT)
                        answer_list = ast.literal_eval(answers)

                        assert len(answer_list) == (evidence_length - 1)

                        connect_response = TextProcessingTools.replace_third_person_with_second_person(evidence_lst[0])
                        for i in range(len(answer_list)):
                            connect_response += f' {answer_list[i]}, {TextProcessingTools.replace_third_person_with_second_person(evidence_lst[i+1])}'

                        final_dialogue += f"Doctor: {connect_response}\n"
                    elif evidence_length == 1:
                        polish_word = TextProcessingTools.replace_third_person_with_second_person(words)
                        final_dialogue += f"Doctor: {polish_word}\n"
                    else:
                        final_dialogue += f"Doctor: {words}\n"
                        
                elif pat_match:
                    words = pat_match.group(1)
                    evidence_lst = re.findall(r'\[(.*?)\]', words)
                    evidence_length = len(evidence_lst)
                    if evidence_length > 1:
                        CONNECT_PROMPT = f"""
                            I have the following 4 sentences in a list that I want to connect in a natural, flowing order:
                            ['The patient experienced sudden onset of shortness of breath.', 'The chest X-ray showed clear lungs.', 'She was started on bronchodilators and steroids to manage the symptoms.', 'Her condition improved significantly over the next 48 hours.']
                            Could you provide 3 conjunction words to connect these sentences naturally? 
                            The output should be in the format: [word1, word2, word3].
                            Answers: [However, Therefore, As a result]

                            I have the following {evidence_length} sentences in a list that I want to connect in a natural, flowing order:
                            {evidence_lst}
                            Could you provide {evidence_length - 1} conjunction words to connect these sentences naturally? 
                            The output should be in the format: [word1, word2, word3].
                            Answers:
                            """
                        answers = TextProcessingTools.gpt4_response(CONNECT_PROMPT)
                        answer_list = ast.literal_eval(answers)

                        assert len(answer_list) == (evidence_length - 1)

                        connect_response = self.text_process.get_patient_answer(evidence_lst[0])
                        for i in range(len(answer_list)):
                            connect_response += f' {answer_list[i]}, {self.text_process.get_patient_answer(evidence_lst[i+1])}'

                        final_dialogue += f"Patient: {connect_response}\n"

                    elif evidence_length == 1:
                        polish_word = self.text_process.get_patient_answer(words)
                        final_dialogue += f"Patient: {polish_word}\n"
                    else:
                        final_dialogue += f"Patient: {words}\n"

            refine_dialogue_dict[case_key] = final_dialogue
        
        TextProcessingTools.save_json(f'./output/final/{self.pub_id}.json', refine_dialogue_dict)
                        
        
    def paraphrase_dialogue(self):
        from nltk.corpus import wordnet as wn
        from nltk.corpus import brown
        from collections import Counter

        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
        nltk.download('brown', quiet=True)

        word_freq = Counter(brown.words())


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



# input_files = os.listdir("./input/full_report/")
# input_files.reverse() 
# output_files = os.listdir("./output/stage1/")
# pid_files = os.listdir("./output/stage1_mc/")

# output_files_lst = [output_file.split(".")[0] for output_file in output_files]
# pid_lst = [pid_f.split(".")[0] for pid_f in pid_files]

# with open('unqualified_2.pkl', 'rb') as file:
#     unqualified_list = pickle.load(file)

# unqualified_list = ['5385457', '9137060', '6277656', '9758034', '10477898', '7199548', '9264904', '3776570', '7501640', '7034452', '7099780', '9455203', '10769979', '5943106', '6935170', '6466908', '5829091', '9190750', '6834403', '10483363', '9777632', '7967652', '6372673', '3408286', '8019644', '9405108', '2910884', '5054737', '6683940', '6868814', '10907016', '9236448', '4364685', '4223596', '8844807', '5578354', '6589948', '10698862', '8262314', '10411822', '7517452', '4614822', '8547661', '8387889', '4231051', '5966531', '7878915', '3906152', '10659192', '6692717', '5837349', '9324652', '6023015', '9858533', '6548057', '10424280', '3039970', '9778251', '8354451', '4480246', '11049876', '6727397', '8052180', '4797186', '9859322', '2940776', '6434444', '5359445', '6380226', '10562628', '10673596', '4338407', '4972865', '9935731', '5590475', '6618132', '11068106', '4251168', '5278304', '9938787', '8105944', '10122526', '10570992', '7057081', '8929994', '10891437', '8818152', '6769743', '3429563', '5078930', '7067821', '7875809', '4246642', '5406054', '10629414', '3852713', '7141722', '7722305', '9601381', '10973880']


# count = 0
# re_pid_lst = []
# for input_file in input_files:
#     file_id = input_file.split(".")[0]
#     if file_id in unqualified_list and file_id not in output_files_lst:
#         processor = MedicalDialogueProcessor(
#         f"./input/full_report/{input_file}", file_id
#         )
#         re_pid = processor.generate_evidence()
#         if re_pid != "yes":
#             re_pid_lst.append(re_pid) 
#         else:
#             count += 1
#         if count == 1000:
#             break
# # import pickle
# print(len(re_pid_lst))
# print(re_pid_lst)
# with open('unqualified_2.pkl', 'wb') as file:
#     pickle.dump(re_pid_lst, file)

# processor.generate_evidence()
# processor.generate_dialogue()
# processor.reload_dialogue()
# processor.refine_dialogue()
# processor.eval_dialogue()
