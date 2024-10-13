import spacy
import scispacy
from scispacy.linking import EntityLinker


nlp = spacy.load("en_core_sci_md")
nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "umls"})


texts = [
    "A diagnosis of eosinophilic endomyocarditis was thus confirmed.",
    "Based on the result, acute erythroid leukemia (AML-M6) was diagnosed.",
    "Histopathologic examinations of huge mass and remnant stalk revealed normal mature adipocytes compatible with those of lipoma.",
    "The postnatal macroscopic findings confirmed the diagnosis of sacrococcygeal teratoma (Figure 3).",
    "He presented with symptoms indicative of myocardial infarction.",
    "MRI scans show no signs of glioblastoma.",
    "The patient denies any history of diabetes mellitus.",
    "Her condition improved after treatment, ruling out pneumonia."
]

def extract_diagnosis(text):
    doc = nlp(text)

    medical_entities = set()
    for ent in doc.ents:
        if ent._.umls_ents:
            medical_entities.add(ent.text)


    negations = {"no", "not", "without", "denies", "negative", "rule out", "ruling out"}
    negated_entities = set()

    for token in doc:
        if token.lower_ in negations:
            for child in token.children:
                if child.ent_type_:
                    negated_entities.add(child.text)
            for descendant in token.subtree:
                if descendant.ent_type_:
                    negated_entities.add(descendant.text)
            for ancestor in token.ancestors:
                if ancestor.ent_type_:
                    negated_entities.add(ancestor.text)


    diagnoses = medical_entities - negated_entities


    return list(diagnoses)


for text in texts:
    diagnoses = extract_diagnosis(text)
    print(f"Text: {text}")
    print(f"Extracted Diagnosis: {diagnoses}")
    print("-" * 40)

