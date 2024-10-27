import os
import json
from bs4 import BeautifulSoup

INPUT_FOLDER = "./input/PMC_patient_data"
OUTPUT_FOLDER = "./input/full_report"
input_files = [f for f in os.listdir(INPUT_FOLDER) if not f.startswith('.')]
pid_files = [f for f in os.listdir("./output/stage1") if not f.startswith('.')]
pid_lst = [pf.split(".")[0] for pf in pid_files]
import pickle

# with open('unqualified_2.pkl', 'rb') as file:
#     qualified_list = pickle.load(file)

# qualified_list = ['5385457', '9137060', '6277656', '9758034', '10477898', '7199548', '9264904', '3776570', '7501640', '7034452', '7099780', '9455203', '10769979', '5943106', '6935170', '6466908', '5829091', '9190750', '6834403', '10483363', '9777632', '7967652', '6372673', '3408286', '8019644', '9405108', '2910884', '5054737', '6683940', '6868814', '10907016', '9236448', '4364685', '4223596', '8844807', '5578354', '6589948', '10698862', '8262314', '10411822', '7517452', '4614822', '8547661', '8387889', '4231051', '5966531', '7878915', '3906152', '10659192', '6692717', '5837349', '9324652', '6023015', '9858533', '6548057', '10424280', '3039970', '9778251', '8354451', '4480246', '11049876', '6727397', '8052180', '4797186', '9859322', '2940776', '6434444', '5359445', '6380226', '10562628', '10673596', '4338407', '4972865', '9935731', '5590475', '6618132', '11068106', '4251168', '5278304', '9938787', '8105944', '10122526', '10570992', '7057081', '8929994', '10891437', '8818152', '6769743', '3429563', '5078930', '7067821', '7875809', '4246642', '5406054', '10629414', '3852713', '7141722', '7722305', '9601381', '10973880']

for input_f in input_files:
    pid = input_f.split(".")[0]
    # if pid in qualified_list:
    with open(os.path.join(INPUT_FOLDER, input_f), 'r', encoding='utf-8') as file:
        xml_content = file.read()

    soup = BeautifulSoup(xml_content, 'xml')
    # print(soup)

    def extract_section_content(section, title_lst=[]):
        section_dict = {}
        title_tag = section.find('title')

        if title_tag and title_tag not in title_lst:
            title_lst.append(title_tag)
            main_title = title_tag.text.strip()
            section_dict[main_title] = {}

            paragraphs = section.find_all('p', recursive=False)
            content = ' '.join(p.text.strip() for p in paragraphs if p.text)
            
            if content:
                section_dict[main_title]['content'] = content

            subsections = section.find_all('sec', recursive=False)
            for subsection in subsections:
                subtitle_dict = extract_section_content(subsection, abs_title)
                section_dict[main_title].update(subtitle_dict)
        
        return section_dict

    reports_dict = {}


    abstract = soup.find('abstract')
    if abstract:
        abs_title = []
        abs_dict = {}

        sections = abstract.find_all('sec')
        
        for section in sections:
            title_tag = section.find('title')
            if title_tag:
                abs_title.append(title_tag)
                section_title = title_tag.text.strip()
                section_content = ' '.join(p.text.strip() for p in section.find_all('p'))
                abs_dict[section_title] = section_content
        reports_dict['abs'] = abs_dict

    body = soup.find('body')
    sections = body.find_all('sec') if body else []

    # assert sections != [], f"No Body Part in {pid}" 
    if sections != []:
        for section in sections:
            report_content = extract_section_content(section)
            reports_dict.update(report_content)


        with open(os.path.join(OUTPUT_FOLDER, f"{pid}.json"), 'w') as json_file:
            json.dump(reports_dict, json_file, indent=4)


# import pprint
# pprint.pprint(reports_dict)
