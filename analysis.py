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

def get_all_correlations():
    final_data = pd.read_csv('../data/final/final_data.csv')
    #Get the correlations for each athletic measurement for each position
    corr_df = pd.DataFrame()
    for pos in final_data['Position'].unique():
        #Get just the data for that position
        pos_data = final_data[final_data['Position'] == pos]
        #Get the correlations
        pos_corr = pos_data.corr().reset_index(drop = False)
        #Create the position and sample size columns
        pos_corr['Position'] = [pos] * len(pos_corr)
        pos_corr['Sample Size'] = len(pos_data)
        corr_df = pd.concat([corr_df, pos_corr[['Position', 'index', 'Sample Size', 'Normalized Value']]], axis=0)
    corr_df = corr_df.reset_index(drop = True)

    corr_df.columns = ['Position', 'Measurement', 'Sample Size', 'Correlation']

    corr_df = corr_df[~(corr_df['Measurement'].isin(['Normalized Value', 'Value']))].reset_index(drop = True)

    corr_df = corr_df.dropna(subset = ['Correlation']).reset_index(drop = True)

    #Save the data
    if not os.path.exists(os.path.abspath('../data/')):
        Logger.debug('Making data folder')
        os.mkdir(os.path.abspath('../data'))
    if not os.path.exists(os.path.abspath('../data/results/')):
        Logger.debug('Making results data folder')
        os.mkdir(os.path.abspath('../data/results'))

    corr_df.to_csv(os.path.abspath('../data/results/correlations.csv'), index=False)

    return corr_df
    
