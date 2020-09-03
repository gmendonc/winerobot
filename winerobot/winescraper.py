from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER, logging
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup as bs
from progress.bar import IncrementalBar 
import os
import platform
import urllib.parse
import re
import pandas as pd
import numpy as np
import configparser
import logging

# Criando o logger
logger = logging.getLogger('Winerobot.Winescraper')
# Criando o Configurador
config = configparser.ConfigParser()
config['COLUMNS'] = {
    'wine_name': 'wine_name',
    'link': 'link',
    'country': 'country',
    'type': 'type',
    'grape': 'grape',
    'classification': 'classification',
    'description': 'description',
    'evaluation': 'evaluation',
    'rating_count': 'rating_count',
    'lowest_price': 'lowest_price',
    'full_price': 'full_price',
    'discount': 'discount',
    'vivino_name': 'vivino_name',
    'vivino_link': 'vivino_link',
    'vivino_score': 'vivino_score',
    'vivino_rating': 'vivino_rating',
    'vivino_price': 'vivino_price'
}
config.read('config.ini')

# Classe Scraper
class Scraper:
    """

    Classe para gerenciar o browser Seleniun e o BeatifulSoup.
    """
 
    def init_browser(self):
        options = Options()
        options.headless = True
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('window-size=1920x1080')
        options.add_argument('start-maximized') # 
        options.add_argument('disable-infobars')
        options.add_argument("--disable-extensions")
        options.add_argument("--log-level=3")
        
        try:
            if platform.system() == 'Windows':
                CHROMEDRIVER_PATH = os.path.join('.chromedriver','bin', 'chromedriver')
                self._browser = webdriver.Chrome(CHROMEDRIVER_PATH, options= options)
            else:
                self._browser = webdriver.Chrome(options= options)
        except Exception as e:
            logger.exception('Erro no Webdriver')
            raise e
    def load_winepage(self, url):
        logger.debug('Carregando a pagina')
        self._browser.get(url)
        delay = 10 # seconds
        logger.debug("Page is ready!")
    
    def get_soup(self, url):
        try:
            self.load_winepage(url)
            logger.debug('Carregando BeautifulSoup')
            soup = bs(self._browser.page_source, 'html.parser')
            return soup
        except:
            logger.exception('Erro no carregamento da página')
    
    def close(self):
        self._browser.quit()

        
    def __init__(self):
        try:
            self.init_browser()
        except Exception as e:
            logger.exception('Falha ao iniciar o browser')
            raise e


class Wine:
    """
    Classe para representar cada vinho
    """

    def find_name(self):
        try:
            soup = self._soup
            name = soup.find('div', class_='ProductDisplay-name').a['title']
            self._name = name
            logger.debug(f'Nome do Vinho: {self._name}')
        except AttributeError as error:
            logger.warning("Nome não encontrado")
            raise
            
    def find_link(self):
        try:
            soup = self._soup
            href = soup.find('div', class_='ProductDisplay-name').a['href']
            link = "wine.com.br" + href.replace('//','/vinhos/')
            self._link = link
            logger.debug(f'HREF: {href}')
            logger.debug(f'Link: {self._link}')
        except AttributeError as error:
            logger.warning("Link não encontrado")
            raise
            
    def find_country(self):
        try:
            soup = self._soup
            country = soup.find(class_="Country").span.text
            self._country = country
            logger.debug(f'País: {self._country}')
        except AttributeError as error:
            logger.warning("País não encontrado")
            raise
            
    def find_type(self):
        try:
            soup = self._soup
            type = soup.find(class_="ProductDisplay-type").span.text
            self._type = type
            logger.debug(f'Tipo: {self._type}')
        except AttributeError as error:
            logger.debug("Tipo não encontrado")
            raise
            
    def find_description(self):
        try:
            soup = self._soup
            description = soup.find(class_="ProductDisplay-descriptionText").text
            self._description = description
            logger.debug(f'Descrição: {self._description}')
        except AttributeError as error:
            logger.warning("Descrição não encontrada")
            raise
            
    def find_rating(self):
        try:
            soup = self._soup
            rating = soup.find('div',class_='Rating')
            evaluation_tag = rating.find(class_='evaluation')
            if (evaluation_tag):
                evaluation = float(re.compile(r"\d.\d").search(evaluation_tag.prettify()).group())
                rating_count = float(re.search(r"\d+", rating.find(class_='Rating-count').text).group())
                self._wine_evaluation = evaluation
                self._wine_rating_count = rating_count
                logger.debug(f'Evaluation: {self._wine_evaluation}')
                logger.debug(f'Rating Count: {self._wine_rating_count}')
        except AttributeError as error:
            logger.warning("Avaliação não encontrada")
            
    def find_price(self):
        try:
            soup = self._soup
            price_box = soup.find(class_="ProductDisplay-priceBox")
            price_str = price_box.find(class_="PriceBoxW-member").find(class_="Price-integer").text + price_box.find(class_="PriceBoxW-member").find(class_="Price-decimal").text
            lowest_price = float(price_str.replace(',','.'))
            price_str = price_box.find(class_="PriceBoxW-listPrice").find(class_="Price-integer").text + price_box.find(class_="PriceBoxW-listPrice").find(class_="Price-decimal").text
            full_price = float(price_str.replace(',','.'))
            discount = 1-float(lowest_price)/float(full_price)
            self._lowest_price = lowest_price
            self._full_price = full_price
            self._discount = discount
            logger.debug(f'Preços: {self._lowest_price}, {self._full_price}, {self._discount}')
        except AttributeError as error:
            logger.warning("Preços não encontrados")
            raise
            
    def find_grape(self):
        try:
            wine_url = 'https://' + self._link
            soup= self._scraper.get_soup(wine_url)
    
            technical_details = soup.find('div', class_='TechnicalDetails')
            tipo_e_uva = technical_details.find('div', class_='TechnicalDetails-description--grape')
            uva = tipo_e_uva.find('div', class_="Right").dd.text

            classificacao_container = technical_details.find('div', class_='TechnicalDetails-description--classification')
            classificacao = classificacao_container.find('div', class_="Right").dd.text

            self._grape = uva
            self._classification = classificacao

            logger.debug(f'Uva e Classificação: {self._grape}, {self._classification}') 
        except AttributeError as error:
            logger.warning("Uva e Classificação não encontrados")
        except:
            logger.warning("Problema ao procurar uva e classificação")
            
    def viv_find_name(self, soup):
        try:
            vivino_name_card = soup.find('span', class_="wine-card__name")
            vivino_name = vivino_name_card.text.replace("\n","")
            vivino_link = 'www.vivino.com'+vivino_name_card.a['href']
            self._vivino_name = vivino_name
            self._vivino_link = vivino_link
            logger.debug(f'Vivino Nome + Link: {self._vivino_name}, {self._vivino_link}')
        except:
            logger.warning('Erro ao buscar o nome do vinho no Vivino')
            raise

    def viv_find_score(self, soup):
        try:
            vivino_average_score_txt = soup.find('div', class_="average__number").text.replace("\n","")
            vivino_average_score = float(vivino_average_score_txt.replace(",","."))
            self._vivino_avg_score = vivino_average_score
            logger.debug(f'Vivino - Nota: {self._vivino_avg_score}')
        except:
            logger.warning(f'{self._name}: Erro ao pesquisar a nota no Vivino')
            raise

    def viv_find_rating(self, soup):
        try:
            vivino_rating_txt = soup.find('div', class_="average__stars").text
            vivino_rating = float(re.search(r"\d+",vivino_rating_txt).group())
            self._vivino_rating = vivino_rating
            logger.debug(f'Vivino - Qtde de avaliações: {self._vivino_rating}')
        except:
            logger.warning(f'{self._name}: Erro ao buscar qtde de avaliações no Vivino')
            raise

    def viv_find_price(self, soup):
        try:
            vivino_price_txt = soup.find('span', class_="wine-price-value").text
            vivino_price = float(vivino_price_txt.replace(",","."))
            self._vivino_price = vivino_price
            logger.debug(f'Vivino - Preço: {self._vivino_price}')
        except:
            logger.debug(f'{self._name}: Erro ao buscar o preço no Vivino')

    def query_vivino(self):

        VIVINO_SEARCH_URL = 'https://www.vivino.com/search/wines?q='
        self._vivino_name = 'indefinido'
        self._vivino_link = 'indefinido'
        self._vivino_avg_score = 0.0
        self._vivino_rating = 0.0
        self._vivino_price = None
        try:
            query_url = urllib.parse.quote(self._name)
            vivino_url = VIVINO_SEARCH_URL+query_url.replace("%20","+")
            logger.info(f'VIVINO - Busca: {vivino_url}')
            vivino_soup = self._scraper.get_soup(vivino_url)
            wine_card_soup = vivino_soup.find('div', class_="wine-card__content")
            self.viv_find_name(wine_card_soup)
            self.viv_find_score(wine_card_soup)
            self.viv_find_rating(wine_card_soup)
            self.viv_find_price(wine_card_soup)
        except:
            logger.warning('Erro ao buscar no Vivino')
            raise

    def get_dict(self):
        dict = {
            'wine_name': self._name,
            'wine_link': self._link,
            'wine_country': self._country,
            'wine_type': self._type,
            'wine_grape': self._grape,
            'wine_class': self._classification,
            'wine_description': self._description,
            'wine_score': self._wine_evaluation,
            'wine_count': self._wine_rating_count,
            'wine_lowest_price': self._lowest_price,
            'wine_full_price': self._full_price,
            'wine_discount': self._discount,
            'vivino_name': self._vivino_name,
            'vivino_link': self._vivino_link,
            'vivino_score': self._vivino_avg_score,
            'vivino_count': self._vivino_rating,
            'vivino_price': self._vivino_price
        }
        return dict

    def get_df(self):
        df_columns = config['COLUMNS']
        properties_list = [[self._name, self._link, self._country, self._type, self._grape, self._classification, self._description, self._wine_evaluation, self._wine_rating_count,
                            self._lowest_price, self._full_price, self._discount, self._vivino_name, self._vivino_link, self._vivino_avg_score, self._vivino_rating, self._vivino_price]]
        df = pd.DataFrame(properties_list, columns = df_columns)
        # Correção de um problema que acontece no Winedetective quando o país está vazio
        df[df_columns['country']] = df.country.replace(np.nan, 'undefined', regex=True)
        df["country"] = df["country"].astype(str)
        return df

    def __init__(self, wine_soup, scraper):
        logger.debug('Criando Objeto Vinho')
        try:
            self._scraper = scraper
            self._soup = wine_soup
            self._name = 'indefinido'
            self.find_name()
            logger.info(f'Vinho: {self._name}')
            self._link = 'indefinido'
            self.find_link()
            self._country = 'indefinido'
            self.find_country()
            self._type = 'indefinido'
            self.find_type()
            self._description = 'indefinido'
            self.find_description()
            self._wine_evaluation = 0
            self._wine_rating_count = 0
            self.find_rating()
            self._lowest_price, self._full_price, self._discount = 0.0, 0.0, 0.0
            self.find_price()
            self._grape, self._classification = 'indefinido', 'indefinido'
            self.find_grape()
            self.query_vivino()
        except:
            if self._name:
                logger.warning(f'Pulando item incompleto: {self._name}')
                raise
            else:
                logger.warning('Pulando item incompleto: sem nome')
                raise
        
    


def is_last_page(soup):
    last_page = True
    pages_list = soup.find('div', class_='Pagination')
    nav_links = pages_list.find_all(class_='Pagination-nav')
    for link in nav_links:
        if link.text == 'Próxima >>':
            last_page = False
    logger.debug(f'LAST PAGE = {last_page}')
    return last_page


# Função process_winepage
def process_winepage(sc, url):
    
    df_columns = config['COLUMNS']
    page_df = pd.DataFrame(columns=df_columns)
    logger.info(f'Processando Página: {url}')
    try:
        page_soup = sc.get_soup(url)
        last_page = is_last_page(page_soup)
    except TimeoutException:
        logger.exception("Loading took too much time!")
        raise
    wine_list = page_soup.find('div', class_='ProductList-content').ul.find_all('li')
    bar = IncrementalBar('Processando', max = len(wine_list))
    for wine_item in wine_list:
        try:
            wine_article = wine_item.find('article', class_='ProductDisplay')
            wine = Wine(wine_article, sc)
            page_df = page_df.append(wine.get_df(), ignore_index=True)
        except:
            logger.warning('Pulando Vinho')
        bar.next()
    print(' ')
    return last_page, page_df
            