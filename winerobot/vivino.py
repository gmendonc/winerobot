from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import perf_counter
import urllib.parse
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import re
import time
import os
import sys


def search_vivino(wine_result= 'result_wine.csv'):

    VIVINO_SEARCH_URL = 'https://www.vivino.com/search/wines?q='

    CHROMEDRIVER_PATH = os.path.join('.chromedriver','bin', 'chromedriver')
    options = Options()
    options.headless = True
    #options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('window-size=1920x1080')
    options.add_argument('start-maximized') # 
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")
    
    browser = webdriver.Chrome(CHROMEDRIVER_PATH, options= options)

    reference_df = pd.read_csv(wine_result)

    lst_vivino_name, lst_vivino_link, lst_vivino_score, lst_vivino_rating, lst_vivino_price = [], [], [], [], []
    lst_original_name = []

    for index, row in reference_df.iterrows():
    
        query_url = urllib.parse.quote(row.wine_name)
        new_url = VIVINO_SEARCH_URL+query_url.replace("%20","+")
    
        #print("Searching...", new_url)
    
        start_time = perf_counter()
    
        try:
            browser.get(new_url)
            vivino_soup_byselenium = bs(browser.page_source,'html.parser')
            vivino_search_item = vivino_soup_byselenium.find('div', class_="wine-card__content")
            vivino_name_card = vivino_search_item.find('span', class_="wine-card__name")
            vivino_name = vivino_name_card.text.replace("\n","")
            lst_original_name.append(row.wine_name)
            lst_vivino_name.append(vivino_name)

            vivino_link = 'www.vivino.com'+vivino_name_card.a['href']
            lst_vivino_link.append(vivino_link)

            vivino_average_score_txt = vivino_search_item.find('div', class_="average__number").text.replace("\n","")
            try:
                vivino_average_score = float(vivino_average_score_txt.replace(",","."))
            except:
                vivino_average_score = None
            lst_vivino_score.append(vivino_average_score)

            try:
                vivino_rating_txt = vivino_search_item.find('div', class_="average__stars").text
                vivino_rating = float(re.search(r"\d+",vivino_rating_txt).group())
            except:
                vivino_rating = None
            lst_vivino_rating.append(vivino_rating)

            try:
                vivino_price_txt = vivino_search_item.find('span', class_="wine-price-value").text
                vivino_price = float(vivino_price_txt.replace(",","."))
            except:
                vivino_price = None
            lst_vivino_price.append(vivino_price)
    
            time.sleep(5)
        except AttributeError as error:
            print(error)
        except:
            print("Erro: {}".format(sys.exc_info()[0]))
            print("Next!")
    
        elapsed_time = perf_counter()-start_time
        #print("tempo: ", elapsed_time)
        
    
    browser.quit()

    df = pd.DataFrame({
        'wine_name' : lst_original_name,
        'vivino_name': lst_vivino_name,
        'vivino_link': lst_vivino_link,
        'vivino_score': lst_vivino_score,
        'vivino_rating': lst_vivino_rating,
        'vivino_price': lst_vivino_price,
    })

    return df

if __name__ == "__main__":
    print('Arquivo de entrada: {}'.format(sys.argv[1]))

    df= search_vivino(sys.argv[1])
    df.to_csv('result_vivino.csv', index= False)