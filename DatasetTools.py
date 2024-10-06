import os
import re
import json
from typing import List, Tuple
from nltk.tokenize import sent_tokenize
from rouge_score import rouge_scorer
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class TextProcessingTools:
    @staticmethod
    def preprocess_text(text: str) -> str:
        return re.sub(r'[^A-Za-z0-9]', '', text)

    @staticmethod
    def is_continuous_match(extracted_sentence: str, document: str) -> bool:
        if extracted_sentence == document:
            return True
        else:
            extracted_sentence_processed = TextProcessingTools.preprocess_text(extracted_sentence)
            document_processed = TextProcessingTools.preprocess_text(document)
            return extracted_sentence_processed in document_processed

    @staticmethod
    def best_match_rouge(sentence: str, article_sentences: List[str]) -> Tuple[str, float]:
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        best_score = 0
        best_sentence = None

        for article_sentence in article_sentences:
            scores = scorer.score(sentence, article_sentence)
            rouge_l_score = scores['rougeL'].fmeasure

            if rouge_l_score > best_score:
                best_score = rouge_l_score
                best_sentence = article_sentence

        return best_sentence, best_score

    @staticmethod
    def gpt4_response(prompt: str) -> str:
        try:
            completion = client.chat.completions.create(model="gpt-4o",
            messages=[{"role": "user", "content": prompt}])
            return completion.choices[0].message.content
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    @staticmethod
    def load_json(file_path: str) -> dict:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)

    @staticmethod
    def save_json(file_path: str, content: dict):
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(content, json_file, ensure_ascii=False, indent=4)

    @staticmethod
    def generate_prefix(qa_pairs):
        return f"""
        Doctor: Hi! How are you feeling today?
        Patient: Hi, doctor. I’m feeling a bit better, but I still have some concerns.

        Doctor: I see, Could you please share a little about yourself, and if you have any medical conditions or allergies?
        Patient: {qa_pairs['1']['cleaned_answer']}
        """

    @staticmethod
    def generate_patient_experience(qa_pairs):
        pe_length = min(5, len(qa_pairs['2']['cleaned_answer']))
        prompt_pe = f"""
        Based on the following patient’s experience, generate a multi-round doctor-patient dialogue (no more than {pe_length} rounds) where the doctor asks questions focusing on the patient's experience, their progression, and any follow-up details. For the patient’s responses, extract answers from the provided 'Patient's experience', do not change any words and close them in the brackets.
        Output format example:
        Doctor: When did you first notice the symptoms related to your eyes? 
        Patient: ['He claimed to have bilateral metamorphopsia with generalized body aches about 3\xa0h postvaccination.', 'His myalgia and backache resolved after 1 day, and his right eye metamorphosia resolved after 3 days.']

        Patient's experience:
        {qa_pairs['2']['cleaned_answer']}
        """
        return TextProcessingTools.gpt4_response(prompt_pe)

    @staticmethod
    def generate_patient_symptoms(qa_pairs):
        ps_length = min(5, len(qa_pairs['3']['cleaned_answer']))
        prompt_ps = f"""
        Based on the following patient’s symptoms, generate a multi-round doctor-patient dialogue (no more than {ps_length} rounds) where the doctor asks questions focusing on the patient's symptoms, their progression, and any follow-up details. For the patient’s responses, extract answers from the provided 'Patient's symptoms', do not change any words and close them in the brackets.
        Output format example:
        Doctor: When did you first notice the symptoms related to your eyes? 
        Patient: ['He claimed to have bilateral metamorphopsia with generalized body aches about 3\xa0h postvaccination.', 'His myalgia and backache resolved after 1 day, and his right eye metamorphosia resolved after 3 days.']

        Patient's symptoms:
        {qa_pairs['3']['cleaned_answer']}
        """
        return TextProcessingTools.gpt4_response(prompt_ps)

    @staticmethod
    def generate_image_analysis(qa_pairs):
        prompt_image = f"""
        Based on the following patient’s image analysis, generate a multi-round doctor-patient dialogue (no more than 3 rounds) where the doctor extracts the anlysis from the provided 'Patient's image analysis', do not change any words and close them in the brackets. For the patient’s responses, it should be natural and consistent with the doctor's analysis.
        Output format example:
        Doctor: ['(A)Fundus photograph, autofluorescence and ocular coherence tomography findings at 10 days post vaccination.','There was hyperfluroescence at the macula in venous phase of FFA and hypocyanescence at the macula on ICGA.']
        Patient: Yeah, I see.

        Patient's image analysis: 
        {qa_pairs['4']['cleaned_answer']}
        """
        return TextProcessingTools.gpt4_response(prompt_image)

    @staticmethod
    def generate_examination(qa_pairs):
        examination_length = min(5, len(qa_pairs['5']['cleaned_answer']))
        prompt_examination = f"""
        Based on the following patient’s examination, generate a multi-round doctor-patient dialogue (no more than {examination_length} rounds) where the doctor extracts the anlysis from the provided 'Patient's examination', do not change any words and close them in the brackets. For the patient’s responses, it should be natural and consistent with the doctor's analysis.
        Output format example:
        Doctor: ['(A)Fundus photograph, autofluorescence and ocular coherence tomography findings at 10 days post vaccination.','There was hyperfluroescence at the macula in venous phase of FFA and hypocyanescence at the macula on ICGA.']
        Patient: Yeah, I see.

        Patient's examination: 
        {qa_pairs['5']['cleaned_answer']}
        """
        return TextProcessingTools.gpt4_response(prompt_examination)

    @staticmethod
    def generate_suggestions(qa_pairs):
        if "$No$" in qa_pairs['6']['cleaned_answer']:
            suggestion = f"Doctor: {qa_pairs['6']['cleaned_answer']}\nPatient: Got it, Thanks!"
        else:
            suggestion = f"Doctor: {qa_pairs['6']['cleaned_answer']}\nPatient: Will do. Thank you, doctor.\nDoctor: You're welcome. Take care, and don’t hesitate to reach out if you have any more concerns."
        
        return suggestion
