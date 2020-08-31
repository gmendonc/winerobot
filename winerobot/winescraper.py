from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER, logging
from bs4 import BeautifulSoup as bs
import os
import urllib.parse

import logging

# Criando o logger
logger = logging.getLogger('Winerobot.Winescraper')
# Criando os handlers
##c_handler = logging.StreamHandler()
##c_handler.setLevel(logging.DEBUG)
##f_handler = logging.FileHandler('file.log', mode = 'a', encoding='UTF-8')
##c_handler.setLevel(logging.DEBUG)
## Criando os formatters
##c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
##c_handler.setFormatter(c_format)
##f_handler.setFormatter(c_format)
# Adicionando handler ao logger
##logger.addHandler(c_handler)
##logger.addHandler(f_handler)

# Classe Scraper
class Scraper:
    """

    Classe para gerenciar o browser Seleniun e o BeatifulSoup.
    """
 
    def init_browser(self):
        CHROMEDRIVER_PATH = os.path.join('.chromedriver','bin', 'chromedriver')
        options = Options()
        options.headless = False
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('window-size=1920x1080')
        options.add_argument('start-maximized') # 
        options.add_argument('disable-infobars')
        options.add_argument("--disable-extensions")
        LOGGER.setLevel(logging.WARNING)
    
        try:
            self._browser = webdriver.Chrome(CHROMEDRIVER_PATH, options= options)
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
        self._browser.close()

        
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
            logger.warning(f'Nome do Vinho: {self._name}')
        except AttributeError as error:
            logger.error("Nome não encontrado")
            

    def find_link(self):
        try:
            soup = self._soup
            href = soup.find('div', class_='ProductDisplay-name').a['href']
            link = "wine.com.br" + href.replace('//','/vinhos/')
            self._link = link
            logger.warning(f'HREF: {href}')
            logger.warning(f'Link: {self._link}')
        except AttributeError as error:
            logger.error("Link não encontrado")
            
    
    def find_country(self):
        try:
            soup = self._soup
            country = soup.find(class_="Country").span.text
            self._country = country
            logger.warning(f'País: {self._country}')
        except AttributeError as error:
            logger.error("País não encontrado")
            

    def find_type(self):
        try:
            soup = self._soup
            type = soup.find(class_="ProductDisplay-type").span.text
            self._type = type
            logger.debug(f'Tipo: {self._type}')
        except AttributeError as error:
            logger.warning("Tipo não encontrado")
            

    def find_description(self):
        try:
            soup = self._soup
            description = soup.find(class_="ProductDisplay-descriptionText").text
            self._description = description
            logger.warning(f'Descrição: {self._description}')
        except AttributeError as error:
            logger.error("Descrição não encontrada")
            

    def find_rating(self):
        try:
            soup = self._soup
            rating = soup.find('div',class_='Rating')
            evaluation_tag = rating.find('evaluation-tag')
            if (evaluation_tag):
                evaluation = float(re.compile(r"\d.\d").search(wine_evaluation_tag.prettify()).group())
                rating_count = float(re.search(r"\d+", wine_rating.find(class_='Rating-count').text).group())
                self._wine_evaluation = evaluation
                self._wine_rating_count = rating_count
                logger.warning(f'Evaluation: {self._wine_evaluation}')
                logger.warning(f'Rating Count: {self._wine_rating_count}')
        except AttributeError as error:
            logger.error("Avaliação não encontrada")
            

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
            logger.warning(f'Preços: {self._lowest_price}, {self._full_price}, {self._discount}')
        except AttributeError as error:
            logger.error("Preços não encontrados")
            

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

            logger.warning(f'Uva e Classificação: {self._grape}, {self._classification}') 
        except AttributeError as error:
            logger.error("Uva e Classificação não encontrados")
        except:
            logger.error("Problema ao procurar uva e classificação")
            
    def query_vivino(self):

        VIVINO_SEARCH_URL = 'https://www.vivino.com/search/wines?q='
        self._vivino_name = 'indefinido'
        self._vivino_link = 'indefinido'
        self._vivino_avg_score = None
        self._vivino_rating = None
        self._vivino_price = None
        try:
            query_url = urllib.parse.quote(self._name)
            vivino_url = VIVINO_SEARCH_URL+query_url.replace("%20","+")
            soup = self._scraper.get_soup(vivino_url)
            self.viv_find_name(soup)
            self.viv_find_link(soup)
            self.viv_find_score(soup)
            self.viv_find_rating(soup)
            self.viv_find_price(soup)
        except:
            logger.error('Erro ao buscar no Vivino')

    def __init__(self, wine_soup, scraper):
        logger.info('Criando Objeto Vinho')
        try:
            self._scraper = scraper
            self._soup = wine_soup
            self._name = 'indefinido'
            self.find_name()
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
                logger.exception(f'Pulando item incompleto: {self._name}')
                raise
            else:
                logger.exception('Pulando item incompleto: sem nome')
                raise
 



# Função process_winepage
def process_winepage(sc, url):
    
    try:
        page_soup = sc.get_soup(url)
    except TimeoutException:
        logger.exception("Loading took too much time!")
        raise
    wine_list = page_soup.find('div', class_='ProductList-content').ul.find_all('li')
    for wine_item in wine_list:
        try:
            wine_article = wine_item.find('article', class_='ProductDisplay')
            wine = Wine(wine_article, sc)
        except:
            logger.error('Erro no processamento da página')
            