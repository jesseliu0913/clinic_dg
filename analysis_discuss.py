import os
import json
from DatasetTools import TextProcessingTools


INPUT_FOLDER = "./input/full_report/"
DIAG_FOLDER = "./output/stage1_parse/"
OUTPUT_FOLDER = "./output/stage1_mc/"
diag_files = [f for f in os.listdir(DIAG_FOLDER) if not f.startswith('.')]
check_id = ['6307137', '7423352', '5871802', '9891022', '4310103', '9721246', '3166682', '10928238', '8684397', '3423792', '10681787', '9632708', '6007162', '5422748', '10147720', '7035542', '11170102', '7772758', '3023056', '3546909', '2801463', '4471381', '3778795', '9261154', '5096485', '10999433', '10448589', '10747629', '7857668', '5004014', '7513486', '7092767', '4531757', '6159050', '3796926']

FIRST_QUERY = f"""
Task: Please identify and list all sentences in the provided paragraph that explain why a specific diagnosis (e.g., AT) is made instead of other possible diagnoses (e.g., PJRT, AVNRT). For each sentence, clearly state the diagnosis that is being ruled out, followed by the reason for exclusion. List all ruled out diagnosis! Additionally, specify the diagnosis that is confirmed and the sentence(s) from the text that support this conclusion. 

Output Format:
Diagnosis ruled out: [Diagnosis name]
Reason for exclusion: [Sentence from the text that provides the reasoning]
Confirmed diagnosis: [Diagnosis name]
Reason for confirmation: [Sentence(s) from the text that supports the confirmed diagnosis]

Example Output
Diagnosis ruled out: PJRT
Reason for exclusion: "In the present case, the tachycardia started after lengthening of the preceding sinus beat, making PJRT unlikely."
Confirmed diagnosis: AT
Reason for confirmation: "In the present case, there was significant variability in TCL due to varying RP and PR intervals favoring AT as the likely diagnosis."


"""
SECOND_QUERY = f"""
Is there any other ruled-out diagnosis? Also in the same format.
"""

for diag_f in diag_files:
    # print(diag_f)
    pid = diag_f.split(".")[0]
    if pid not in check_id:
    # if pid == "4869430":
        case_lst = []
        file_content = json.load(open(os.path.join(INPUT_FOLDER, diag_f), "r"))
        if file_content != {}:
            for case_key, case_content in file_content.items():
                if "discussion" in case_key.lower():
                    # " ".join(list(case_content.values()))
                    content = str(list(case_content.values())).replace("[", "").replace("]", "")
                    prompt = f"Does this paragraph contain a comparison of diagnoses? If not, directly respond with $NO$.\n{content}"
                    response = TextProcessingTools.gpt4_response(prompt)
                    if "$NO$" not in response:
                        case_dict = {}
                        conversation_history = []
                        prompt1 = FIRST_QUERY + f"\n{content}"
                        response1 = TextProcessingTools.gpt4_response(prompt1)

                        conversation_history.append({"role": "user", "content": prompt1})
                        conversation_history.append({"role": "assistant", "content": response1})
                        prompt2 = SECOND_QUERY 
                        response2 = TextProcessingTools.gpt4_response_whistory(prompt2, conversation_history)

                        case_dict['prompt1'] = prompt1
                        case_dict['response1'] = response1
                        case_dict['prompt2'] = prompt2
                        case_dict['response2'] = response2

                        case_lst.append(case_dict)
                    else:
                        check_id.append(pid)

            if len(case_lst) != 0:
                with open(os.path.join(OUTPUT_FOLDER, f"{pid}.jsonl"), "a") as jsonl_file: 
                    for item in case_lst:
                        jsonl_file.write(json.dumps(item) + '\n') 


      