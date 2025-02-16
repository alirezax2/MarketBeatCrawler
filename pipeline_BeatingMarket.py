
def get_headers():
    """
    Returns a list of user agent strings for different web browsers.

    This function provides a collection of common User-Agent strings that can be used
    for web scraping purposes to rotate between different browser identities. The list
    includes various versions of Chrome, Firefox, Safari, and Edge browsers across
    different operating systems.

    Returns:
        list: A list of strings, each representing a different browser's User-Agent.

    Note:
        Using multiple User-Agent strings can help avoid detection and blocking during
        web scraping operations, but should be used responsibly and in accordance
        with the target website's terms of service.
    """
    headers_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/115.0.1901.188',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/114.0.1823.82',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/113.0.1774.57'
    ]
    return headers_list


def get_targets_marketbeat(Market, Ticker):
    """
    Scrapes price target information from MarketBeat for a given stock.
    This function retrieves the average, low and high price targets for a stock
    from MarketBeat.com by parsing the HTML content of the stock's forecast page.
    Args:
        Market (str): The stock exchange market code (e.g. 'NYSE', 'NASDAQ')
        Ticker (str): The stock ticker symbol (e.g. 'AAPL', 'MSFT')
    Returns:
        tuple: A tuple containing three float values:
            - avgtarget (float): The average price target
            - lowtarget (float): The lowest price target
            - uptarget (float): The highest price target
    Raises:
        None explicitly, but may raise:
            - RequestException: If there's an error making the HTTP request
            - AttributeError: If the expected HTML elements are not found
            - IndexError: If price targets are not found in the expected format
    Note:
        The function uses random User-Agent headers for web scraping to avoid detection.
        Price targets are extracted from text using regex pattern matching for dollar amounts.
    """
    import random
    import re
    import requests
    from bs4 import BeautifulSoup

    url = f'https://www.marketbeat.com/stocks/{Market}/{Ticker}/forecast/'

    headers_list = get_headers()
    headers = { 'User-Agent': f'{headers_list[random.randint(0,len(headers_list))]}' }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    try:
        div_element = soup.find('div', class_='col-md-8 font-9')
        if div_element:
            text = div_element.text.strip()
            targets = re.findall(r'\$\d+(?:\.\d{3})?', text)
    
            if targets:
                avgtarget = float(targets[0].replace('$', ''))
                uptarget = float(targets[1].replace('$', ''))
                lowtarget = float(targets[2].replace('$', ''))
                currentprice = float(targets[3].replace('$', ''))
                return avgtarget, uptarget, lowtarget, currentprice
    except:
        return None

# import pandas as pd
# df = pd.read_csv("hf://datasets/AmirTrader/TradingViewData/america.csv")
    
def load_hf_dataset(csv_filename, token, dataset_name_input):
    """
    Load a CSV dataset from Hugging Face and return as pandas DataFrame
    
    Args:
        csv_filename (str): Name of the CSV file in the dataset
        token (str): Hugging Face authentication token
        
    Returns:
        pandas.DataFrame: DataFrame containing the dataset
    """
    from datasets import load_dataset
    
    try:
        dataset = load_dataset(dataset_name_input, 
                                data_files=csv_filename,
                                split="train",
                                token=token)
        return dataset.to_pandas()
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

#Example
# Ticker = 'XPEV'
# Market = 'NYSE' # 'NASDAQ' or 'NYSE'
# targets = get_targets_marketbeat(Market,Ticker)
# print(f"Target for {Ticker} in Market {Market} are Average {targets[0]} with Max { targets[1]} and Low {targets[2]} and current price {targets[3]}")


# Main code #####################################################################################################################
import os
import pandas as pd
import datetime
from dotenv import load_dotenv

from utils import upload_to_hf_dataset, download_from_hf_dataset

# Load environment variables from .env file
# load_dotenv()

# Get the name of the HuggingFace dataset for TradingView to read from
dataset_name_TradingView_input = os.getenv('dataset_name_TradingView_input')

# Get the Hugging Face API token from the environment; either set in .env file or in the environment directly in GitHub
HF_TOKEN = os.getenv('HF_TOKEN')

#Load lastest TradingView DataSet from HuggingFace Dataset which is always america.csv
# download_from_hf_dataset("america.csv", "AmirTrader/TradingViewData", HF_TOKEN)
df = load_hf_dataset("america.csv", HF_TOKEN, dataset_name_TradingView_input)

df = df.query('`Market Capitalization` > 1e8')
# df.Exchange.unique()
mylst = []
for index,row in df.iterrows():
    Ticker = row['Ticker']
    Market = row['Exchange']
    if Market == 'NYSE ARCA':
        Market = 'NYSE'
    try:
        targets = get_targets_marketbeat(Market,Ticker)
        mylst.append({'Ticker': Ticker, 'AverageTarget': targets[0], 'MaxTarget': targets[1], 'LowTarget': targets[2], 'CurrentPrice': targets[3]} ) 
        print(f"Target for {Ticker} in Market {Market} are Average {targets[0]} with Max { targets[1]} and Low {targets[2]} and current price {targets[3]}")
    except:
        print(f"Error for {Ticker} in Market {Market} ")

df_beatingmarket = pd.DataFrame(mylst)

file_path = fr'./output/beatingmarket-{datetime.datetime.now().strftime("%Y-%m-%d")}.csv'
latest_file_path = fr'./output/beatingmarket.csv'
df_beatingmarket.to_csv(file_path, index=False)
df_beatingmarket.to_csv(latest_file_path, index=False)

dataset_name_BeatingMarket_output = os.getenv('dataset_name_BeatingMarket_output')

# Upload each file to the dataset
upload_to_hf_dataset(file_path, dataset_name_BeatingMarket_output, HF_TOKEN, repo_type="dataset")
upload_to_hf_dataset(latest_file_path, dataset_name_BeatingMarket_output, HF_TOKEN, repo_type="dataset")




