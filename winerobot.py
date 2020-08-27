from winerobot.wine import get_soup, get_num_pages, scrape_soup, get_browser
from winerobot.winescraper import Scraper
import pandas as pd
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import logging

# Logging
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

# Webscrapper do Site da Wine
# Cabeçalhos e Imports

URL_RAIZ="https://www.wine.com.br"
URL_BASE = URL_RAIZ+"/vinhos/{0}/cVINHOS-atTIPO_{1}-p{2}.html"


if __name__ == "__main__":
    # Módulo Principal - Processamento do Site
    wine_df = pd.DataFrame(columns=['wine_name','link','country','type','grape', 'classification', 'description','evaluation','rating_count','lowest_price','full_price','discount'])

    tipos_de_vinho = ['TINTO','BRANCO','ROSE','ESPUMANTE']

    try:
        sc = Scraper()
    except:
        logger.exception('Erro ao iniciar o Scraper')

    for tipo in tipos_de_vinho:
        pages_to_scrape = 4
        current_page = 1
        while (current_page != pages_to_scrape):
    
            logger.debug(f'Vinho {tipo}. Analizando a página {current_page}')

            page_url = URL_BASE.format(tipo.lower(),tipo, current_page)
            process_winepage(sc, page_url)
            
            browser.get(URL_BASE.format(tipo.lower(),tipo, current_page))
            delay = 10 # seconds
            try:
                myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'Pagination')))
                print ("Page is ready!")
            except TimeoutException:
                print ("Loading took too much time!")
    
            wine_soup = get_soup(browser)
    
            if current_page == 1:
                pages_to_scrape = get_num_pages(wine_soup)
    
            new_df = scrape_soup(browser, wine_soup)
            wine_df= wine_df.append(new_df, ignore_index=True)
    
            ###print(current_page)
    
            time.sleep(10)
            current_page += 1
    
    print("Scrape finished.")
    browser.close()
    wine_df.to_csv('result_wine.csv',index=False)