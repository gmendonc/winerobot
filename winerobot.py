from winerobot.wine import get_soup, get_num_pages, scrape_soup, get_browser
import pandas as pd
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# Webscrapper do Site da Wine
# Cabeçalhos e Imports

URL_RAIZ="https://www.wine.com.br"
URL_BASE = URL_RAIZ+"/vinhos/{0}/cVINHOS-atTIPO_{1}-p{2}.html"


if __name__ == "__main__":
    # Módulo Principal - Processamento do Site
    wine_df = pd.DataFrame(columns=['wine_name','link','country','type','grape', 'classification', 'description','evaluation','rating_count','lowest_price','full_price','discount'])

    tipos_de_vinho = ['TINTO','BRANCO','ROSE','ESPUMANTE']

    try:
        browser = get_browser()
    except:
        print('Erro Selenium')

    for tipo in tipos_de_vinho:
        pages_to_scrape = 4
        current_page = 1
        while (current_page != pages_to_scrape):
    
            print('vinho ', tipo, ': Iniciando get_soup pagina ', current_page)
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