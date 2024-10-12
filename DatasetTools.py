import os
import re
import json
import spacy
from nltk.corpus import wordnet as wn
from nltk.corpus import brown
from collections import Counter
from typing import List, Tuple
from nltk.tokenize import sent_tokenize
from rouge_score import rouge_scorer
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
nlp = spacy.load('en_core_web_sm')
word_freq = Counter(brown.words())

class TextProcessingTools:
    def __init__(self):
        self.pronoun_mapping = {
                "he": "I",
                "she": "I",
                "him": "me",
                "her": "me",
                "his": "my",
                "hers": "mine",
                "himself": "myself",
                "herself": "myself",
                "they": "we",
                "them": "us",
                "their": "our",
                "theirs": "ours",
                "themselves": "ourselves",
            }

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

        for sent_idx, article_sentence in enumerate(article_sentences):
            scores = scorer.score(sentence, article_sentence)
            rouge_l_score = scores['rougeL'].fmeasure

            if rouge_l_score > best_score:
                best_score = rouge_l_score
                best_sentence = article_sentence

        return best_sentence, sent_idx

    @staticmethod
    def gpt4_response(prompt: str, max_tokens=1000) -> str:
        try:
            completion = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens  
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
        if "No" in qa_pairs['6']['cleaned_answer']:
            suggestion = f"Doctor: {qa_pairs['6']['cleaned_answer']}\nPatient: Got it, Thanks!"
        else:
            suggestion = f"Doctor: {qa_pairs['6']['cleaned_answer']}\nPatient: Will do. Thank you, doctor.\nDoctor: You're welcome. Take care, and don’t hesitate to reach out if you have any more concerns."
        
        return suggestion

    def replace_pronouns(self, text):
        doc = nlp(text)
        modified_tokens = []

        for token in doc:
            token_lower = token.text.lower()
            if token_lower in self.pronoun_mapping:
                new_token = self.pronoun_mapping[token_lower]
                if token.text[0].isupper():
                    new_token = new_token.capitalize()
                modified_tokens.append(new_token)
            else:
                modified_tokens.append(token.text)

        return " ".join(modified_tokens)

    @staticmethod
    def extract_main_components(text):
        doc = nlp(text)
        subjects = []
        verbs = []
        objects = []

        for chunk in doc.noun_chunks:
            if chunk.root.dep_ in ["nsubj", "nsubjpass"]:
                subjects.append(chunk.text)

        for token in doc:
            if token.pos_ == "VERB":
                aux_neg = [child for child in token.children if child.dep_ in ["aux", "neg", "advmod"]]
                aux_neg = sorted(aux_neg, key=lambda x: x.i)
                verb_tokens = aux_neg + [token]
                verb_phrase = ' '.join([t.text for t in verb_tokens])
                verbs.append(verb_phrase)

        for chunk in doc.noun_chunks:
            if chunk.root.dep_ in ["dobj", "pobj", "obj", "iobj"]:
                objects.append(chunk.text)

        return subjects, verbs, objects

    @staticmethod
    def is_time_related(phrase):
        doc = nlp(phrase)
        if any(ent.label_ in ["DATE", "TIME"] for ent in doc.ents):
            return True
        return bool(re.search(r'\d', phrase))

    @staticmethod
    def contains_number(phrase):
        return bool(re.search(r'\d', phrase))

    def substitute_if_infrequent(self, phrase, replaced_text, threshold=5):
        words = phrase.split()
        new_words = []
        for word in words:
            word_lower = word.lower()
            if word_freq[word_lower] < threshold:
                CONTEXT_PROMPT = f"""
                Within the sentence '{replaced_text}' please replace the word 'bilateral' with an easier-to-understand synonym that has the same meaning, while maintaining the grammatical structure and word type. Only output the changed word.
                Answer: two-side
                Within the sentence '{replaced_text}' please replace the word '{word}' with an easier-to-understand synonym that has the same meaning, while maintaining the grammatical structure and word type. Only output the changed word.
                Answer: 
                """
                replaced_word = self.gpt4_response(CONTEXT_PROMPT, 1)
                new_words.append(replaced_word)
            else:
                new_words.append(word)
        return ' '.join(new_words)

    @staticmethod
    def replace_phrases(sentence, phrase_mapping):
        sorted_phrases = sorted(phrase_mapping.keys(), key=len, reverse=True)
        escaped_phrases = [re.escape(phrase) for phrase in sorted_phrases]
        pattern = re.compile(r'\b(' + '|'.join(escaped_phrases) + r')\b', flags=re.IGNORECASE)

        def replace_match(match):
            original_phrase = match.group(0)
            for key in phrase_mapping:
                if key.lower() == original_phrase.lower():
                    return phrase_mapping[key]
            return original_phrase

        return pattern.sub(replace_match, sentence)

    def get_patient_answer(self, text):
        updated_objects = []

        replaced_text = self.replace_pronouns(text)
        subjects, verbs, objects = self.extract_main_components(replaced_text)

        for obj in objects:
            if self.is_time_related(obj) or self.contains_number(obj):
                updated_objects.append(obj)
            else:
                updated_obj = self.substitute_if_infrequent(obj, replaced_text)
                updated_objects.append(updated_obj)

        phrase_mapping = dict(zip(objects, updated_objects))
        updated_sentence = self.replace_phrases(replaced_text, phrase_mapping)

        modified_sentence = re.sub(r'\((?![^)]*Figure)[^)]*\)', '', updated_sentence)
        modified_sentence = re.sub(r'(?<!Figure)\*', '', modified_sentence)
        modified_sentence = re.sub(r'\s+', ' ', modified_sentence).strip()
        return modified_sentence.replace("[", "").replace("]", "").replace("‘$No$’", 'Nope').strip()

    @staticmethod
    def replace_third_person_with_second_person(text):
        replacements = {
            r"\bhe\b": "you", r"\bshe\b": "you",
            r"\bhim\b": "you", r"\bher\b": "you", 
            r"\bhis\b": "your", r"\bhers\b": "yours", 
        }

        for key, value in replacements.items():
            text = re.sub(key, value, text, flags=re.IGNORECASE)

        modified_sentence = re.sub(r'\((?![^)]*Figure)[^)]*\)', '', text)
        modified_sentence = re.sub(r'(?<!Figure)\*', '', modified_sentence)
        modified_sentence = re.sub(r'\s+', ' ', modified_sentence).strip()
        return modified_sentence.replace("[", "").replace("]", "").replace("‘$No$’", 'Nope').strip()
