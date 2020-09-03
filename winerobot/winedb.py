#Imports
import pandas as pd
import numpy as np
import logging
import sys
from pymongo import MongoClient


# Criando o logger
logger = logging.getLogger('Winerobot.WineDB')

def create_db(file):

    logger.info('Criando Banco de Dados')

    try:
        #Load csv dataset
        logger.debug('Abrindo arquivo')
        data = pd.read_csv(file)

        # Connect to Mongodb
        logger.debug('Conectando ao Mongodb')
        client = MongoClient("mongodb+srv://winemaster:winescrape7@projectw-vkqlx.mongodb.net/test?retryWrites=true&w=majority")
        db = client['winedb']
        collection = db['wines']
        collection.drop()

        logger.debug('Zerando o banco')
        data.reset_index(inplace=True)
        data_dict = data.to_dict("records")

        # Insert collection
        logger.debug('Adicionando coleção')
        collection.insert_many(data_dict)

        logger.info('Atuaização do banco de dados concluída')
    except:
        logger.exception('Erro ao atualizar o banco de dados')
        raise

if __name__ == "__main__":
    print('Arquivo de entrada: {}'.format(sys.argv[1]))
    data = pd.read_csv(sys.argv[1])
    data["country"] = data.country.replace(np.nan, 'undefined', regex=True)
    data["country"] = data["country"].astype(str)
    data.to_csv('result_fixed.csv',index=False)
    create_db('result_fixed.csv')