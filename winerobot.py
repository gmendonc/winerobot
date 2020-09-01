from winerobot.wine import get_soup, get_num_pages, scrape_soup, get_browser
from winerobot.winescraper import Scraper, process_winepage
import pandas as pd
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import logging

# Logging
# Criando o logger
logger = logging.getLogger('Winerobot')
logger.setLevel(logging.DEBUG)
# Criando os handlers
c_handler = logging.StreamHandler()
c_handler.setLevel(logging.ERROR)
f_handler = logging.FileHandler('file.log', mode='w', encoding='UTF-8')
f_handler.setLevel(logging.INFO)
# Criando os formatters
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(c_format)
# Adicionando handler ao logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)


# Webscrapper do Site da Wine
# Cabeçalhos e Imports

URL_RAIZ="https://www.wine.com.br"
URL_BASE = URL_RAIZ+"/vinhos/{0}/cVINHOS-atTIPO_{1}-p{2}.html"


if __name__ == "__main__":
    # Módulo Principal - Processamento do Site
    print('>>>>>>>>>>>>>>INÍCIO DO PROCESSAMENTO <<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    
    #tipos_de_vinho = ['TINTO','BRANCO','ROSE','ESPUMANTE']
    tipos_de_vinho = ['TINTO']
    RESET_CSV = True

    try:
        sc = Scraper()
    except:
        logger.exception('Erro ao iniciar o Scraper')

    for tipo in tipos_de_vinho:
        pages_to_scrape = 4
        current_page = 1
        last_page = False
        print(f'>>> VINHO {tipo}')
        while (not last_page):
    
            logger.info(f'Vinho {tipo}. Analizando a página {current_page}')
            print(f'>>>>> PÁGINA {current_page}')

            page_url = URL_BASE.format(tipo.lower(),tipo, current_page)
            last_page, df = process_winepage(sc, page_url)
            logger.debug(f'Check de última página = {last_page}')
            if RESET_CSV:
                df.to_csv('result.csv', encoding='utf-8',mode='w',index=False)
                RESET_CSV = False
            else:
                df.to_csv('result.csv', encoding='utf-8',mode='a',header=False, index=False)

            
    
#            if current_page == 1:
#                pages_to_scrape = get_num_pages(wine_soup)
    
#            new_df = scrape_soup(browser, wine_soup)
#            wine_df= wine_df.append(new_df, ignore_index=True)
    
            ###print(current_page)
    
            time.sleep(10)
            current_page += 1
    
    print("Scrape finished.")
    sc.close()
#   wine_df.to_csv('result_wine.csv',index=False)