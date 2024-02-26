import json
import pandas as pd
import numpy as np
import os
import sys
import time
sys.path.append('/Users/tevans-barton/AAASideProjects/')
import pfr_scraping
package_directory = os.path.dirname(os.path.abspath(__file__))

import logging
logging.basicConfig(filename='../logger.log', format='%(asctime)s %(levelname)s:%(name)s :: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', encoding='utf-8', level=logging.DEBUG)
Logger = logging.getLogger(__name__)

CONTRACT_URL = 'https://www.spotrac.com/nfl/contracts/sort-value/all-time/draft-year-{y}/limit-2000/'

def get_data():
    """
    Get data from Pro Football Reference and Spotrac
    Arguments:
        None
    Downloads:
        Contract data from Spotrac
        Combine data from Pro Football Reference
    Returns:
        Tuple of DataFrames (combine_df, contract_df)
    """
    Logger.debug('Running get_data')
    #Get data parameters
    with open('../data-params.json') as fh:
        data_cfg = json.load(fh)
    years = data_cfg['years']

    #Get contract data
    contract_df = pd.DataFrame()
    for y in years:
        new_contract_df = __get_contract_data(y)
        new_contract_df['Draft Year'] = [y] * len(new_contract_df)
        contract_df = pd.concat([contract_df, new_contract_df], axis=0)
        time.sleep(10)

    #Get combine data
    combine_df = pd.DataFrame()
    for y in years:
        new_combine_df = pfr_scraping.get_combine_data(y)
        new_combine_df['Draft Year'] = [y] * len(new_combine_df)
        combine_df = pd.concat([combine_df, new_combine_df], axis=0)
        time.sleep(10)

    #Download data
    if not os.path.exists(os.path.abspath('../data/')):
        Logger.debug('Making data folder')
        os.mkdir(os.path.abspath('../data'))
    if not os.path.exists(os.path.abspath('../data/raw/')):
        Logger.debug('Making raw data folder')
        os.mkdir(os.path.abspath('../data/raw'))
    
    contract_df.to_csv(os.path.abspath('../data/raw/contract_data.csv'), index=False)
    combine_df.to_csv(os.path.abspath('../data/raw/combine_data.csv'), index=False)

    Logger.debug('Finished running get_data')
    return (combine_df, contract_df)

def __get_contract_data(draft_year):
    """
    Get contract data from spotrac for a given draft year
    Arguments:
        draft_year: int of draft year
    Returns:
        pd.DataFrame of contract data
    """
    Logger.debug('Running __get_contract_data for draft year: ' + str(draft_year))
    url = CONTRACT_URL.format(y=draft_year)
    try:
        contract_df = pd.read_html(url)[0]
    except Exception as e:
        Logger.error(e)
        raise Exception('Unable to get rushing data from Pro Football Reference '+str(e))
    contract_df = __clean_contract_data(contract_df)
    Logger.debug('Finished running __get_contract_data for draft year: ' + str(draft_year))
    return contract_df


def __clean_contract_data(contract_df):
    """
    Clean contract data
    Arguments:
        contract_df: pd.DataFrame of contract data
    Returns:
        pd.DataFrame of cleaned contract data
    """
    df = contract_df.copy()

    #Drop rank column
    df = df.drop(['Rank'], axis=1)

    #Rename columns
    df.columns = ['Player', 'Age at Signing', 'Years', 'Value', 'AAV', 'Signing Bonus', 'Guaranteed at Signing', 'Practical Guaranteed']

    #Clean player names
    df['Player'] = df['Player'].str.split('  ', expand = True)[0]
    df['Contract Start Year'] = df['Player'].str.split('  ', expand = True)[1].str.split('|', expand = True)[1].str.split('-', expand = True)[0]

    #Clean non-money characters (commas, dollar signs, etc.)
    df['Value'] = df['Value'].str.replace('[^0-9]', '', regex=True).astype(float)
    df['AAV'] = df['AAV'].str.replace('[^0-9]', '', regex=True).astype(float)
    df['Signing Bonus'] = df['Signing Bonus'].str.replace('[^0-9]', '', regex=True).astype(float)
    df['Guaranteed at Signing'] = df['Guaranteed at Signing'].str.replace('[^0-9]', '', regex=True).astype(float)
    df['Practical Guaranteed'] = df['Practical Guaranteed'].str.replace('[^0-9]', '', regex=True).astype(float)

    df = df[['Player', 'Contract Start Year', 'Age at Signing', 'Years', 'Value', 'AAV', 'Signing Bonus', 'Guaranteed at Signing', 'Practical Guaranteed']]

    return df