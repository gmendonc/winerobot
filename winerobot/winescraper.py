from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs

import logging

# Criando o logger
logger = logging.getLogger(__name__)
# Criando os handlers
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
# Criando os formatters
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
# Adicionando handler ao logger
logger.addHandler(c_handler)

# Classe Scraper
class Scraper:
    """
    Classe para gerenciar o browser Seleniun e o BeatifulSoup.
    """
    def __init__(self):
        try:
            init_browser()
        except Exception as e:
            logger.exception('Falha ao iniciar o browser')
            raise e

    def init_browser():
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
            _browser = webdriver.Chrome(CHROMEDRIVER_PATH, options= options)
        except Exception as e:
            logger.exception('Erro no Webdriver')
            raise e
    def load_winepage(url):
        logger.debug('Carregando a pagina')
        self._browser.get(url)
        delay = 10 # seconds
        try:
            myElem = WebDriverWait(self._browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'Pagination')))
            logger.debug("Page is ready!")
        except TimeoutException:
            logger.exception("Loading took too much time!")
            raise
    
    def get_soup(self, url):
        try:
            load_winepage(url)
            logger.debug('Carregando BeautifulSoup')
            soup = bs(self._browser.page_source, 'html.parser')
            return soup
        except:
            logger.error('Erro no carregamento da página')


class Wine:
    """
    Classe para representar cada vinho
    """
    def __init__(self, wine_soup):
        try:
            self._soup = wine_soup
            self._name = 'indefinido'
            find_name()
            self._link = 'indefinido'
            find_link()
            self._country = 'indefinido'
            find_country()
            self._type = 'indefinido'
            find_type()
            self._description = 'indefinido'
            find_description()
            self._wine_evaluation = 0
            self._wine_rating_count = 0
            find_rating()
            self._lowest_price, self._full_price, self._discount = 0.0, 0.0, 0.0
            find_price()
            self._grape, self._classification = 'indefinido', 'indefinido'
            find_grape()
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
            wine = Wine(wine_article)