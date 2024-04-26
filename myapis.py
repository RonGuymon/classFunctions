#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains custom functions to get data using APIs:
ChatGPT
Bureau of Labor Statistics

Setting an environmental variable
First, generate an api key from your account here: https://platform.openai.com/api-keys

You can do this so that you do not have to share your apiKey in your code. An environmental variable resides on your computer. The way you set it differs between Mac/Linux and Windows. Here's the steps for Mac using terminal:

This creates a line in the .zshrc file: echo "export OPEN_API_KEY=<apiKey>" >> ~/.zshrc
Test if it exists: cat ~./zshrc
Set it permanently: source ~/.zshrc
Completely close and restart Jupyter if it was open


Created on Mon Apr  1 16:05:29 2024

@author: rnguymon
"""
#%% Modules for more than one function
import os # For getting api key from environment variables
#%% gpt_query
'''
I use the ChatGPT API for this function, which will pass a query into ChatGPT.

Here is the documentation: https://platform.openai.com/docs/api-reference

Here's the Python repo on Github: https://github.com/openai/openai-python
'''
from openai import OpenAI # pip install openai

def gpt_query(role = 'user'
              , prompt = ''
              , apiKey = os.environ.get("OPEN_API_KEY")):
    '''
    Passes a query to ChatGPT and receives a response. 
    
    You have to know the series id number. You can find some by going to the 
    prices page, https://www.bls.gov/data/#prices, and then clicking on the 
    Top Picks link.

    For example, the series id numbers for the Chained CPI are next to the
    names here: https://data.bls.gov/cgi-bin/surveymost?su

    You can register for a public API key here: 
        https://www.bls.gov/developers/home.htm

    Parameters
    ----------
    role : STR, optional
        The default is 'user'.
    prompt : TYPE, optional
        The default is '', but it should be replaced with a meaningful prompt.

    Returns
    -------
    STR
        Returns a text string. You can use the ast module to convert text to
        Python code.
        
    Example
    -------
    The example below returns text that can be used to create a dataframe of journal entries.
    
    mp = f'Create 10 accounting journal entries during {m}, 2024, for a company that sells large\
earth moving equipment. There should be no income summary entries. Each entry should have a field for date, description,\
debit account, debit amount, credit account, credit amount. Each entry should be separated by a comma such that it should have this format: ["date1", "description1",\
"debit account 1", "debit amount 1", "credit account 1", "credit amount 1"], ["date2", "description2",\
"debit account 2", "debit amount 2", "credit account 2", "credit amount 2"]'
    t2 = gpt_query(prompt = mp)
    t3 = '[' + (t2) + (']')
    t3 = t3.replace('\n', '')
    mtl = ast.literal_eval(t3)
    tdf = pd.DataFrame(mtl, columns = ['date', 'description', 'debit account', 'debit amount', 
                                       'credit account', 'credit amount'])

    '''
    client = OpenAI(api_key=apiKey)
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": role,
            "content": prompt,
        }
    ],
    model="gpt-3.5-turbo")
    return chat_completion.choices[0].message.content.strip()
#%%% Test gpt_query
#%% get_bls_data
# See example here: https://www.bls.gov/developers/api_python.htm#python2
# Signatures: https://www.bls.gov/developers/api_signature_v2.htm
import datetime as dt
import requests
import json
import pandas as pd
import math


def get_bls_data(startYear = 2000, endYear = dt.date.today().year, 
                 yearInterval = 20, serieslist=['SUUR0000SA0', 'SUUR0000SAF'],
                 apiKey = os.environ.get('BLS_API_KEY')):
    '''
    Parameters
    ----------
    startYear : INT
        The beginning year for getting data. The default is 1990.
    endYear : INT
        The ending year for getting data. The default is dt.date.today().year.
    yearInterval : INT
        The number of years to get at a time. The default is 20 because
        that's the max you can get with an api key.
    serieslist : [STR]
        A list that contains the series ID numbers. No more than 50 ID numbers
        with an api key.
    apiKey : STR
        The api key that you can get for free by registering. The default is 
        the one that I registered for using my illinois email address.

    Returns
    -------
    df : Pandas DataFrame
        A dataframe with four columns: seriesid, year, period, value.
        
    Example
    -------
    my_cpi = (pd.DataFrame({'Chained CPI - All items': 'SUUR0000SA0',
              'Chained CPI - Food and Beverages': 'SUUR0000SAF'}
                           , index=['seriesid'])
              .T
              .reset_index(names='metric'))
    
    # Get the data
    cpidf = get_bls_data(startYear=1999, 
                         serieslist=my_cpi.seriesid.tolist())
    
    # Add in the descriptive lables
    cpidf_long = cpidf.merge(my_cpi, how='left', on='seriesid')

    '''
    # Calculate iterations needed
    yearDif = endYear - startYear
    iterations = math.ceil(yearDif/yearInterval)
    
    df = pd.DataFrame()
    for i in range(iterations):
        if i > endYear:
            break
        # Get Data
        iyears = list(range(startYear, startYear+yearInterval))
        headers = {'Content-type': 'application/json'}
        data = json.dumps({"seriesid": serieslist,
                           "startyear":str(iyears[0]), 
                           "endyear":str(iyears[-1]),
                          'registrationkey': apiKey})
        p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', 
                          data=data, headers=headers)
        json_data = json.loads(p.text)
        
        # Parse data and put into dataframe
        myi = 0
        for series in json_data['Results']['series']:
            for item in series['data']:
                tdf =  pd.DataFrame({'seriesid': series['seriesID'],
                                     'year': item['year'],
                                     'period': item['period'],
                                     'value': item['value']},
                                    index = [myi])
                df = pd.concat([df, tdf])
                myi += 1
        startYear += yearInterval
    df.sort_values(['seriesid', 'year', 'period'], inplace=True)
    return df
