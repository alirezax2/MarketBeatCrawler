import random
import re
import requests
from bs4 import BeautifulSoup


Ticker = 'ARE'

def get_targets_marketbeat(Ticker):
    url = f'https://www.marketbeat.com/stocks/NYSE/{Ticker}/forecast/'

    headers_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/115.0.1901.188',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/114.0.1823.82',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/113.0.1774.57'
    ]

    headers = { 'User-Agent': f'{headers_list[random.randint(0,len(headers_list))]}' }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    div_element = soup.find('div', class_='col-md-8 font-9')
    if div_element:
        text = div_element.text.strip()
        targets = re.findall(r'\$\d+(?:\.\d{2})?', text)
   
        if targets:
            avgtarget = float(targets[0].replace('$', ''))
            lowtarget = float(targets[1].replace('$', ''))
            uptarget = float(targets[2].replace('$', ''))
            return avgtarget, lowtarget, uptarget


targets = get_targets_marketbeat(Ticker)
targets[0], targets[1], targets[2]

