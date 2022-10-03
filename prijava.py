import csv
import requests as req 
from bs4 import BeautifulSoup

OUTPUT_FILE_NAME = 'polozeni.csv'
LOGIN_URL = 'https://studportal.pmf.kg.ac.rs/authentication/login'
PASSED_EXAMS_URL = 'https://studportal.pmf.kg.ac.rs/ispiti/svi-ispiti'
FILTER_KEYS = ['ГС', 'Предмет', 'Оцена', 'Датум', 'ЕСПБ']

def main():

    with req.Session() as session:
        while True:
            response = session.post(LOGIN_URL, get_creds())
            result = session.get(PASSED_EXAMS_URL, cookies=response.cookies)
            txt = result.text.replace('\n','').replace('\t','')
            soup = BeautifulSoup(txt, 'html.parser')
            exams = soup.find(id='ispiti')

            if exams == None:
                print('\nProvided credentials are not valid. Please try again.\n')
                continue

            # Get all rows in HTML tag table
            exams_table_rows = exams.find('table').find_all('tr')
            
            header = extract_header(exams_table_rows)
            data = extract_data(exams_table_rows, header)
            filtered_data = filter_by_keys(data)
            export_as_csv(filtered_data, FILTER_KEYS)
            break

# For testing
def _get_creds():
    return {'username':'', 'password':''}

def get_creds():
    creds = {'username':'', 'password':''}
    creds['username'] = input('Enter your username: ')
    creds['password'] = input('Enter your password: ')

    return creds

def extract_header(table_rows): # TODO delete
    '''Extract header items'''

    header_items = list()
    for item in table_rows[0]:
        try:
            txt = item.get_text()
            if txt != '' and txt != ' ':
                header_items.append(txt.strip())
        except:
            continue
    
    return header_items

def filter_by_keys(data, keys_to_add=FILTER_KEYS):
    return [{key:val for key, val in exam.items() if key in keys_to_add } for exam in data]

def extract_data(table_rows, header):
    '''Extract data'''

    data = list()
    html_rows = table_rows[1:]
    for hrow in html_rows:
        row = list()
        for hdata in hrow:
            try:
                row.append(hdata.get_text())
            except:
                continue
        data.append(row)
    return [dict(zip(header, exam)) for exam in data] 

def export_as_csv(data, header=FILTER_KEYS, fname=OUTPUT_FILE_NAME):
    with open(OUTPUT_FILE_NAME, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header)

        writer.writeheader()
        writer.writerows(data)
    
    print(f'\nData is successfully exported to \'{OUTPUT_FILE_NAME}\'')

if __name__ == '__main__':
    main()
