import os
import json
from bs4 import BeautifulSoup

INPUT_FOLDER = "./input/PMC_patient_data"
OUTPUT_FOLDER = "./input/full_report"
input_files = [f for f in os.listdir(INPUT_FOLDER) if not f.startswith('.')]

for input_f in input_files:
    pid = input_f.split(".")[0]
    with open(os.path.join(INPUT_FOLDER, input_f), 'r', encoding='utf-8') as file:
        xml_content = file.read()

    soup = BeautifulSoup(xml_content, 'xml')
    # print(soup)

    def extract_section_content(section):
        section_dict = {}
        title_tag = section.find('title')

        if title_tag:
            main_title = title_tag.text.strip()
            section_dict[main_title] = {}

            paragraphs = section.find_all('p', recursive=False)
            content = ' '.join(p.text.strip() for p in paragraphs if p.text)
            
            if content:
                section_dict[main_title]['content'] = content

            subsections = section.find_all('sec', recursive=False)
            for subsection in subsections:
                subtitle_dict = extract_section_content(subsection)
                section_dict[main_title].update(subtitle_dict)
        
        return section_dict

    reports_dict = {}

    abstract = soup.find('abstract')
    if abstract:
        abs_dict = {}

        title_tag = abstract.find('title')
        if title_tag:
            abs_dict['title'] = title_tag.text.strip() 

        abs_content = ' '.join(p.text.strip() for p in abstract.find_all('p'))
        abs_dict['content'] = abs_content

        reports_dict['abs'] = abs_dict

    sections = soup.find_all('sec')
    for section in sections:
        report_content = extract_section_content(section)
        reports_dict.update(report_content)


    with open(os.path.join(OUTPUT_FOLDER, f"{pid}.json"), 'w') as json_file:
        json.dump(reports_dict, json_file, indent=4)

# import pprint
# pprint.pprint(reports_dict)
