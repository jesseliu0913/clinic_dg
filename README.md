# Clinic_DG

## General Questions:
- **Question**: Describe the patient's personal information.
- **Question**: Describe the patient's experience.
- **Question**: Did you notice any symptoms, such as a fever, cough, or respiratory issues?
- **Question**: What does the imaging (only provide figure explanation here) suggest?
- **Question**: What does the examination suggest?
- **Question**: Are there any suggestions?

---

## Pipeline:
1. **Stage 1**: Use the general questions to retrieve the evidence list from the provided case report.
2. **Stage 2**: Generate questions or responses for one or multiple pieces of evidence and combine them into a dialogue.
3. **Stage 3**: Combine the separate dialogues into one. At this step, all the main information is extracted from the case report.
4. **Final Stage**: Order and polish the dialogue.

---

## Evaluation Metrics:

### Model 1:
- **ROUGE Scores**:
  - ROUGE-1: Precision = 0.7776, Recall = 0.6403, F1 = 0.7023
  - ROUGE-2: Precision = 0.5194, Recall = 0.4276, F1 = 0.4691
  - ROUGE-L: Precision = 0.6837, Recall = 0.5630, F1 = 0.6175
- **BLEU Score**: 35.71
- **BERTScore**:
  - Precision = 0.9043
  - Recall = 0.8675
  - F1 = 0.8855

### Model 2:
- **ROUGE Scores**:
  - ROUGE-1: Precision = 0.9128, Recall = 0.7872, F1 = 0.8453
  - ROUGE-2: Precision = 0.7548, Recall = 0.6507, F1 = 0.6989
  - ROUGE-L: Precision = 0.8447, Recall = 0.7284, F1 = 0.7823
- **BLEU Score**: 54.25
- **BERTScore**:
  - Precision = 0.9221
  - Recall = 0.8930
  - F1 = 0.9073

### Model 3:
- **ROUGE Scores**:
  - ROUGE-1: Precision = 0.7893, Recall = 0.8520, F1 = 0.8194
  - ROUGE-2: Precision = 0.6577, Recall = 0.7101, F1 = 0.6829
  - ROUGE-L: Precision = 0.7726, Recall = 0.8339, F1 = 0.8021
- **BLEU Score**: 58.84
- **BERTScore**:
  - Precision = 0.9372
  - Recall = 0.9048
  - F1 = 0.9207

### Model 4:
- **ROUGE Scores**:
  - ROUGE-1: Precision = 0.8416, Recall = 0.8260, F1 = 0.8337
  - ROUGE-2: Precision = 0.7085, Recall = 0.6953, F1 = 0.7019
  - ROUGE-L: Precision = 0.7967, Recall = 0.7819, F1 = 0.7892
- **BLEU Score**: 59.29
- **BERTScore**:
  - Precision = 0.9226
  - Recall = 0.9065
  - F1 = 0.9145
