import requests
from bs4 import BeautifulSoup

url = 'http://dndlookup.dartmouth.edu/datapage_dartmouth.php'

def lookup(name):
    results = []
    if not name:
        return results

    undergrad_params = {'name': name + " 1", 'fmat': '1'}
    ug_params = {'name': name + " ug", 'fmat': '1'}

    undergrad_response = requests.get(url, params=undergrad_params)
    ug_response = requests.get(url, params=ug_params)

    undergrad_html = BeautifulSoup(undergrad_response.text)
    ug_html = BeautifulSoup(ug_response.text)

    if undergrad_html.find('span'):
        results.extend([s.text for s in undergrad_html.findAll("span")])

    if undergrad_html.find('a'):
        result = undergrad_html.text
        results.append(result[result.index("Name:") + 6:result.index("Email:")])

    if ug_html.find('span'):
        results.extend([s.text for s in ug_html.findAll("span")])

    if ug_html.find('a'):
        result = ug_html.text
        results.append(result[result.index("Name:") + 6:result.index("Email:")])

    return results
