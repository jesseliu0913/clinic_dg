from bs4 import BeautifulSoup

pid = "10747629"
with open(f'./input/PMC_patient_data/{pid}.xml', 'r', encoding='utf-8') as file:
    xml_content = file.read()


soup = BeautifulSoup(xml_content, 'xml')


title = soup.find('article-title')
print('Title:', title.text if title else 'Title not found')

abstract = soup.find('abstract')
if abstract:
    paragraphs = abstract.find_all('p')
    abstract_text = ' '.join(p.text.strip() for p in paragraphs if p.text)
    print('Abstract:', abstract_text)
else:
    print('Abstract not found')
