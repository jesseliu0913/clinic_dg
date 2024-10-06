# clinic_dg

PIPELINE:
Stage 1: Using the general question to retrieve the evidence list from the provided case report

Stage 2: Generate the question or response for one or multiple pieces of evidence and combine them into a dialogue.

Stage 3: combine the seperate dialogue into one. Until this step, all main information is extract from the case report

Final: Order and polish the dialogue.


ROUGE Scores: {'rouge1': Score(precision=0.7775510204081633, recall=0.6403361344537815, fmeasure=0.7023041474654378), 'rouge2': Score(precision=0.5194274028629857, recall=0.4276094276094276, fmeasure=0.46906740535549407), 'rougeL': Score(precision=0.6836734693877551, 
recall=0.5630252100840336, fmeasure=0.6175115207373272)}

BLEU Score: 35.71032676995603

BERTScore - Precision: 0.9043044447898865 Recall: 0.86748206615448 F1: 0.8855106234550476


ROUGE Scores: {'rouge1': Score(precision=0.9127659574468086, recall=0.7871559633027523, fmeasure=0.845320197044335), 'rouge2': Score(precision=0.7547974413646056, recall=0.6507352941176471, fmeasure=0.6989141164856861), 'rougeL': Score(precision=0.8446808510638298, recall=0.728440366972477, fmeasure=0.7822660098522167)}

BLEU Score: 54.247457746069024

BERTScore - Precision: 0.9221127033233643 Recall: 0.8929579257965088 F1: 0.907301127910614


ROUGE Scores: {'rouge1': Score(precision=0.7892976588628763, recall=0.851985559566787, fmeasure=0.8194444444444444), 'rouge2': Score(precision=0.6577181208053692, recall=0.7101449275362319, fmeasure=0.6829268292682927), 'rougeL': Score(precision=0.7725752508361204, recall=0.8339350180505415, fmeasure=0.8020833333333334)}

BLEU Score: 58.835939977161345

BERTScore - Precision: 0.9371599555015564 Recall: 0.9048126935958862 F1: 0.920702338218689


ROUGE Scores: {'rouge1': Score(precision=0.8416075650118203, recall=0.8259860788863109, fmeasure=0.8337236533957846), 'rouge2': Score(precision=0.7085308056872038, recall=0.6953488372093023, fmeasure=0.7018779342723005), 'rougeL': Score(precision=0.7966903073286052, recall=0.7819025522041764, fmeasure=0.7892271662763466)}

BLEU Score: 59.285214262457345

BERTScore - Precision: 0.9226124882698059 Recall: 0.9064506888389587 F1: 0.9144601821899414
