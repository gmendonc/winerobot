from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import re
import time
import os


def get_browser():

    CHROMEDRIVER_PATH = os.path.join('.chromedriver','bin', 'chromedriver')
    options = Options()
    options.headless = True
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('window-size=1920x1080')
    options.add_argument('start-maximized') # 
    options.add_argument('disable-infobars')
    options.add_argument("--disable-extensions")
    
    try:
        browser = webdriver.Chrome(CHROMEDRIVER_PATH, options= options)
    except:
        print("webdriver falhou")
        raise
    return browser

def get_soup(browser):
    
    print("Iniciando session_get")
    
    try:
        soup = bs(browser.page_source, 'html.parser')
        return soup
    except:
        print("get_browser falhou")
        raise

def get_num_pages(soup):
    
    pages_list = soup.find('div', class_='Pagination').ul.find_all('li')
    num_pages = int(pages_list[len(pages_list)-1].a.text) + 1
    
    return num_pages

def scrape_technical_details(browser, wine_url):
    browser.get(wine_url)
    wine_soup= get_soup(browser)
    
    technical_details = wine_soup.find('div', class_='TechnicalDetails')
    tipo_e_uva = technical_details.find('div', class_='TechnicalDetails-description--grape')
    uva = tipo_e_uva.find('div', class_="Right").dd.text

    classificacao_container = technical_details.find('div', class_='TechnicalDetails-description--classification')
    classificacao = classificacao_container.find('div', class_="Right").dd.text

    print('{}: {}'.format(classificacao, uva))    
    
    return uva, classificacao
    
def scrape_soup(browser, soup):
    
    list_name=[]
    list_link, list_country, list_type, list_description= [], [], [], []
    list_evaluation, list_rating_count= [], []
    list_lowest_price, list_full_price, list_discount= [], [], []
    list_grape, list_class= [], []
    
    wine_list = soup.find('div', class_='ProductList-content').ul.find_all('li')

    for wine_item in wine_list:
        
        try:
            wine = wine_item.find('article', class_='ProductDisplay')

            wine_name = wine.find('div', class_='ProductDisplay-name').a['title']
            wine_link = "wine.com.br" + wine.find('div', class_='ProductDisplay-name').a['href']
            wine_country = wine.find(class_="Country").span.text
            wine_type = wine.find(class_="ProductDisplay-type").span.text
            wine_description = wine.find(class_="ProductDisplay-descriptionText").text
        
            wine_rating = wine.find('div',class_='Rating')
            wine_evaluation_tag = wine_rating.find('evaluation-tag')
            if (wine_evaluation_tag):
                wine_evaluation = float(re.compile(r"\d.\d").search(wine_evaluation_tag.prettify()).group())
                wine_rating_count = float(re.search(r"\d+", wine_rating.find(class_='Rating-count').text).group())
            else:
                wine_evaluation = 0
                wine_rating_count = 0
    
        
            price_box = wine.find(class_="ProductDisplay-priceBox")

            lowest_price = float(price_box.find(class_="Price--lowestPrice").find(class_="Price-raw").text)
            full_price = float(price_box.find(class_="Price--fullPrice").find(class_="Price-raw").text)
            discount = 1-float(lowest_price)/float(full_price)
            try:
                grape, classification = scrape_technical_details(browser, 'https://' + wine_link)
            except:
                grape, classification= 'indefinido', 'indefinido'
            
        except:
            if wine_name:
                print('skip incomplete item:', wine_name)
                continue
            else:
                print("skip incomplete item: no name")
                continue
        
        list_name.append(wine_name)
        list_link.append(wine_link)
        list_country.append(wine_country)
        list_type.append(wine_type)
        list_description.append(wine_description)
        
        list_evaluation.append(wine_evaluation)
        list_rating_count.append(wine_rating_count)

        list_lowest_price.append(lowest_price)
        list_full_price.append(full_price)
        list_discount.append(discount)
        list_grape.append(grape)
        list_class.append(classification)
        
        ###print(wine_name,";", wine_evaluation, ";", wine_rating_count, ";", wine_country, ";", wine_type, ";", lowest_price, ";", full_price, ";", discount,";", wine_link)
    
    df = pd.DataFrame({
        'wine_name': list_name,
        'link': list_link,
        'country': list_country,
        'type': list_type,
        'grape': list_grape,
        'classification': list_class,
        'description': list_description,
        'evaluation': list_evaluation,
        'rating_count': list_rating_count,
        'lowest_price': list_lowest_price,
        'full_price': list_full_price,
        'discount': list_discount
    })
    
    return df