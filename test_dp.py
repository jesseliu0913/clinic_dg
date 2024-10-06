import spacy
import scispacy
from scispacy.umls_linker import UmlsEntityLinker
from nltk.corpus import wordnet


nlp = spacy.load("en_core_sci_sm")
linker = UmlsEntityLinker(resolve_abbreviations=True)
nlp.add_pipe(linker)

medical_simplifications = {
    "cured": "healed",
    "carefully follow": "follow closely",
    "medication": "medicine",
    "instructions": "advice"
}


def get_pos_tags(doc):
    return [(token.text, token.pos_) for token in doc]


def get_syntactic_structure(doc):
    subject = [chunk.text for chunk in doc.noun_chunks if chunk.root.dep_ == "nsubj"]
    verbs = [token.text for token in doc if token.pos_ == "VERB"]
    objects = [chunk.text for chunk in doc.noun_chunks if chunk.root.dep_ == "dobj"]
    return subject, verbs, objects


def get_synonym(word):
    synonyms = wordnet.synsets(word)
    if synonyms:
        return synonyms[0].lemmas()[0].name()
    return word

def synonym_replacement(doc):
    new_sentence = []
    for token in doc:
        # Replace only adjectives, nouns, and verbs
        if token.pos_ in {"ADJ", "NOUN", "VERB"}:
            simplified_word = get_synonym(token.text.lower())
            new_sentence.append(simplified_word)
        else:
            new_sentence.append(token.text)
    return " ".join(new_sentence)


def get_umls_explanation(entity):
    if entity._.umls_ents:
        umls_concept_id = entity._.umls_ents[0][0]
        concept = linker.umls.cui_to_entity[umls_concept_id]
        return concept.name if len(concept.name) < 40 else concept.name.split(",")[0]
    return entity.text

def replace_medical_terms_with_umls_explanations(doc):
    new_sentence = []
    current_index = 0
    for entity in doc.ents:
        new_sentence.append(doc.text[current_index:entity.start_char])
        explanation = get_umls_explanation(entity)
        new_sentence.append(explanation)
        current_index = entity.end_char
    new_sentence.append(doc.text[current_index:])
    return "".join(new_sentence)


def simplify_sentence(doc):
    new_sentence = []
    for token in doc:
        if not token.is_stop:  
            new_sentence.append(token.text)
    return " ".join(new_sentence)


def template_based_rewriting(subject, verbs, objects):
    if subject and verbs and objects:
        return f"{subject[0]} must {verbs[0]} the {objects[0]} and {verbs[1]} to heal completely."
    return ""


def remove_redundancies(sentence):
    return sentence.replace("completely heal", "heal")


def process_sentence(sentence):
    doc = nlp(sentence)
    pos_tags = get_pos_tags(doc)
    
    subject, verbs, objects = get_syntactic_structure(doc)
    
    sentence_with_synonyms = synonym_replacement(doc)
    
    sentence_with_umls = replace_medical_terms_with_umls_explanations(doc)
    
    simplified_sentence = simplify_sentence(doc)

    rewritten_sentence = template_based_rewriting(subject, verbs, objects)
    
    final_sentence = remove_redundancies(rewritten_sentence)
    
    return {
        "pos_tags": pos_tags,
        "subject": subject,
        "verbs": verbs,
        "objects": objects,
        "sentence_with_synonyms": sentence_with_synonyms,
        "sentence_with_umls": sentence_with_umls,
        "simplified_sentence": simplified_sentence,
        "rewritten_sentence": rewritten_sentence,
        "final_sentence": final_sentence
    }


sentence = (
    "To be fully cured, the patient must regularly take the prescribed medication and carefully follow all of the doctor's instructions."
)


result = process_sentence(sentence)


print("Tokenization and POS Tagging:", result["pos_tags"])
print("Subject:", result["subject"])
print("Verbs:", result["verbs"])
print("Objects:", result["objects"])
print("Synonym Replacement:", result["sentence_with_synonyms"])
print("Medical Term Simplification:", result["sentence_with_umls"])
print("Sentence Simplification:", result["simplified_sentence"])
print("Template-based Rewriting:", result["rewritten_sentence"])
print("Final Sentence (After Redundancy Removal):", result["final_sentence"])
