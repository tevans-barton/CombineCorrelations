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

def create_final_data():
    contracts = pd.read_csv('../data/raw/contract_data.csv')
    combine = pd.read_csv('../data/raw/combine_data.csv')

    #Get the second contract each player received
    second_contracts = contracts.groupby('Player').nth(1)

    #Merge with the combine data
    merged_data = combine.merge(second_contracts, left_on='Player', right_on='Player', how='inner').reset_index(drop=True)

    #Simplify the draft year to one column
    merged_data['Draft Year'] = merged_data['Draft Year_x']
    merged_data = merged_data.drop(['Draft Year_x', 'Draft Year_y'], axis=1)

    #Get a normalized version of the contract 'Value' based on previous contracts
    merged_data['Normalized Value'] = __normalize_contract_by_position(merged_data, contracts)

    #Cut down columns to just necessary columns
    merged_data = merged_data[['Player', 'Pos', 'Ht', 'Wt', '40yd', 'Vertical', 'Bench', 'Broad Jump', '3Cone', 'Shuttle', 'Pick', 'Value', 'Normalized Value']]

    #Save the data
    if not os.path.exists(os.path.abspath('../data/')):
        Logger.debug('Making data folder')
        os.mkdir(os.path.abspath('../data'))
    if not os.path.exists(os.path.abspath('../data/final/')):
        Logger.debug('Making final data folder')
        os.mkdir(os.path.abspath('../data/final'))
    merged_data.to_csv(os.path.abspath('../data/final/final_data.csv'), index=False)

    return merged_data



def __normalize_contract_by_position(merged_df, contracts):
    """
    Helper function to normalize the contract value column, by looking at where each value is, normalized in 
    reference to all contracts for that player's position between the 2000 season and 
    the year that said contract was signed
    Arguments:
        merged_df: DataFrame, the combined DataFrame of combine and contract data
        contracts: DataFrame, the raw contract data
    Returns:
        Series, the normalized contract values
    """
    vals = []
    for row in merged_df.iterrows():
        row = row[1]
        position = row['Pos']
        year = row['Contract Start Year']
        player_names = merged_df[merged_df['Pos'] == position]['Player'].unique()
        relevant_data = contracts[(contracts['Contract Start Year'] < year) & (contracts['Player'].isin(player_names))]
        val_mean = relevant_data['Value'].mean()
        val_std = relevant_data['Value'].std()
        try:
            normalized_value = (row['Value'] - val_mean) / val_std
            vals.append(normalized_value)
        except Exception as e:
            Logger.error(f'Error normalizing contract value for {row["Player"]}: {e}')
            vals.append(np.nan)
    return pd.Series(vals)

