"""
Stage 1: Using the general question to retrieve the evidence list from the provided case report
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
        self.answer_dict = TextProcessingTools.load_json(self.answer_file)
        self.clean_answer_dict = {}
        self.dialog_realco_dict = {}

    def generate_evidence(self):
        for key in self.answer_dict:
            answer_text = self.answer_dict[key]['answer']
            article_text = self.data[key]
            article_sentences = sent_tokenize(article_text)
            cleaned_answer_text = answer_text.replace('*', '')

            qa_pairs = re.findall(
                r'Question:(.*?)\nAnswer:(.*?)(?=\nQuestion:|\Z)',
                cleaned_answer_text,
                re.DOTALL
            )

            self.clean_answer_dict[key] = {}
            for i, (question, answer) in enumerate(qa_pairs, 1):
                self.clean_answer_dict[key][i] = {'question': question.strip(), 'answer': answer.strip()}
                answer_sentences = sent_tokenize(answer)
                clean_answer = []

                for token_answer in answer_sentences:
                    found_match = any(
                        TextProcessingTools.is_continuous_match(token_answer, sent)
                        for sent in article_sentences
                    )
                    if found_match:
                        clean_answer.append(token_answer)
                    elif TextProcessingTools.preprocess_text(token_answer) == 'No':
                        clean_answer.append(token_answer)
                    else:
                        best_sentence, _ = TextProcessingTools.best_match_rouge(token_answer, article_sentences)
                        clean_answer.append(best_sentence)

                self.clean_answer_dict[key][i]['cleaned_answer'] = clean_answer

        folder_path = os.path.join(self.answer_folder, "stage1")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        TextProcessingTools.save_json(f'{folder_path}/{self.pub_id}.json', self.clean_answer_dict)

    def generate_dialogue(self):
        for key in self.clean_answer_dict:
            dialog_dict = {}
            qa_pairs = self.clean_answer_dict[key]

            dialog_dict['prefix'] = TextProcessingTools.generate_prefix(qa_pairs)
            dialog_dict['patient_experience'] = TextProcessingTools.generate_patient_experience(qa_pairs)
            dialog_dict['patient_symptoms'] = TextProcessingTools.generate_patient_symptoms(qa_pairs)
            dialog_dict['image'] = TextProcessingTools.generate_image_analysis(qa_pairs)
            dialog_dict['examination'] = TextProcessingTools.generate_examination(qa_pairs)
            dialog_dict['suggestion'] = TextProcessingTools.generate_suggestions(qa_pairs)

            self.dialog_realco_dict[key] = dialog_dict
        
        folder_path = os.path.join(self.answer_folder, "stage2")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        TextProcessingTools.save_json(f'{folder_path}/{self.pub_id}.json', self.dialog_realco_dict)


processor = MedicalDialogueProcessor(
    '/path/to/test_optical.json',
    '/path/to/case_answer.json'
)
processor.generate_evidence()
processor.generate_dialogue()
