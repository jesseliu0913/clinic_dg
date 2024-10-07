import spacy
import re
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import brown
from collections import Counter

nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('brown', quiet=True)

nlp = spacy.load('en_core_web_sm')

word_freq = Counter(brown.words())

pronoun_mapping = {
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

def replace_pronouns(text):
    doc = nlp(text)
    modified_tokens = []

    for token in doc:
        token_lower = token.text.lower()
        if token_lower in pronoun_mapping:
            new_token = pronoun_mapping[token_lower]
            if token.text[0].isupper():
                new_token = new_token.capitalize()
            modified_tokens.append(new_token)
        else:
            modified_tokens.append(token.text)

    return " ".join(modified_tokens)

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

def is_time_related(phrase):
    doc = nlp(phrase)
    if any(ent.label_ in ["DATE", "TIME"] for ent in doc.ents):
        return True
    return bool(re.search(r'\d', phrase))

def contains_number(phrase):
    return bool(re.search(r'\d', phrase))

def substitute_if_infrequent(phrase, threshold=5):
    words = phrase.split()
    new_words = []
    for word in words:
        word_lower = word.lower()
        if word_freq[word_lower] < threshold:
            synsets = wn.synsets(word_lower)
            if synsets:
                synonym_found = False
                for syn in synsets:
                    for lemma in syn.lemmas():
                        synonym = lemma.name().replace('_', ' ')
                        if synonym.lower() != word_lower:
                            new_words.append(synonym)
                            synonym_found = True
                            break
                    if synonym_found:
                        break
                if not synonym_found:
                    new_words.append(word)
            else:
                new_words.append(word)
        else:
            new_words.append(word)
    return ' '.join(new_words)

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

sentence_1 = "He presented to the ophthalmology clinic with left eye 10 days after vaccination."
sentence_2 = "She will visit the hospital tomorrow at 3 PM."
sentence_3 = "Prior to this episode, he did not have any ocular symptoms."
sentence_4 = "He claimed to have bilateral metamorphopsia with generalized body aches about 3 h postvaccination."

modified_sentence_1 = replace_pronouns(sentence_1)
modified_sentence_2 = replace_pronouns(sentence_2)
modified_sentence_3 = replace_pronouns(sentence_3)
modified_sentence_4 = replace_pronouns(sentence_4)

subjects_1, verbs_1, objects_1 = extract_main_components(modified_sentence_1)
subjects_2, verbs_2, objects_2 = extract_main_components(modified_sentence_2)
subjects_3, verbs_3, objects_3 = extract_main_components(modified_sentence_3)
subjects_4, verbs_4, objects_4 = extract_main_components(modified_sentence_4)

print("Modified Sentence 1:")
print(modified_sentence_1)
print("Subjects:", subjects_1)
print("Verbs:", verbs_1)
print("Objects:", objects_1)

print("\nModified Sentence 2:")
print(modified_sentence_2)
print("Subjects:", subjects_2)
print("Verbs:", verbs_2)
print("Objects:", objects_2)

print("\nModified Sentence 3:")
print(modified_sentence_3)
print("Subjects:", subjects_3)
print("Verbs:", verbs_3)
print("Objects:", objects_3)

updated_objects = []
for obj in objects_4:
    if is_time_related(obj) or contains_number(obj):
        updated_objects.append(obj)
    else:
        updated_obj = substitute_if_infrequent(obj)
        updated_objects.append(updated_obj)
        print(f"Original: {obj}, Updated: {updated_obj}")

phrase_mapping = dict(zip(objects_4, updated_objects))

updated_sentence_4 = replace_phrases(modified_sentence_4, phrase_mapping)

print("\nModified Sentence 4:")
print(modified_sentence_4)
print("Subjects:", subjects_4)
print("Verbs:", verbs_4)
print("Objects:", objects_4)

print("\nUpdated Sentence 4:")
print(updated_sentence_4)
