import os
import re
import json
from typing import List, Tuple
from nltk.tokenize import sent_tokenize
from rouge_score import rouge_scorer
import openai

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
        openai.api_key = os.getenv("OPENAI_API_KEY")
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
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
        Doctor: Could you please share a little about yourself, and if you have any medical conditions or allergies?
        Patient: {qa_pairs['1']['cleaned_answer']}
        """

    @staticmethod
    def generate_patient_experience(qa_pairs):
        pe_length = min(5, len(qa_pairs['2']['cleaned_answer']))
        prompt_pe = f"""
        Based on the following patient’s experience, generate a multi-round doctor-patient dialogue (no more than {pe_length} rounds) focusing on the patient's experience.
        Patient's experience: {qa_pairs['2']['cleaned_answer']}
        """
        return TextProcessingTools.gpt4_response(prompt_pe)

    @staticmethod
    def generate_patient_symptoms(qa_pairs):
        ps_length = min(5, len(qa_pairs['3']['cleaned_answer']))
        prompt_ps = f"""
        Based on the following patient’s symptoms, generate a multi-round doctor-patient dialogue (no more than {ps_length} rounds).
        Patient's symptoms: {qa_pairs['3']['cleaned_answer']}
        """
        return TextProcessingTools.gpt4_response(prompt_ps)

    @staticmethod
    def generate_image_analysis(qa_pairs):
        prompt_image = f"""
        Based on the following patient’s image analysis, generate a multi-round doctor-patient dialogue.
        Patient's image analysis: {qa_pairs['4']['cleaned_answer']}
        """
        return TextProcessingTools.gpt4_response(prompt_image)

    @staticmethod
    def generate_examination(qa_pairs):
        examination_length = min(5, len(qa_pairs['5']['cleaned_answer']))
        prompt_examination = f"""
        Based on the following patient’s examination, generate a multi-round doctor-patient dialogue.
        Patient's examination: {qa_pairs['5']['cleaned_answer']}
        """
        return TextProcessingTools.gpt4_response(prompt_examination)

    @staticmethod
    def generate_suggestions(qa_pairs):
        return f"Doctor: [{qa_pairs['6']['cleaned_answer']}]\nPatient: Will do. Thank you, doctor."
