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
              , apiKey = os.environ.get("OPEN_API_KEY")
              , my_model = "gpt-3.5-turbo"):
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
    apiKey : STR
        You can get one from here: https://platform.openai.com/playground/chat?models=gpt-4o
    my_model : STR, default = '3.5-turbo'
        Each model has a different billing rate. The available models are: 
            GPT-4 Models:
                gpt-4-0613
                gpt-4-1106-preview
                gpt-4-0125-preview
                gpt-4-turbo
                gpt-4-turbo-2024-04-09
                gpt-4-turbo-preview
                gpt-4-32k-0613
            GPT-3.5 Models:
                gpt-3.5-turbo-0613
                gpt-3.5-turbo-1106
                gpt-3.5-turbo-0125
                gpt-3.5-turbo-16k
                gpt-3.5-turbo-instruct-0914

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
    model = my_model)
    return chat_completion.choices[0].message.content.strip()
#%%% Test gpt_query
my_prompt = '''
Tell me about the different types of dashboards there are
and create a taxonomy that I can use to teach others.
'''
# q35 = gpt_query(prompt = my_prompt)
# print(q35)
# q40613 = gpt_query(prompt = my_prompt,
#                 my_model = 'gpt-4-0613')
# print(q40613)
#%% get_bls_data
# See example here: https://www.bls.gov/developers/api_python.htm#python2
# Signatures: https://www.bls.gov/developers/api_signature_v2.htm
import datetime as dt
import requests
import json
import pandas as pd
import math
import io


def get_bls_data(startYear = 2000, endYear = dt.date.today().year, 
                 yearInterval = 20, serieslist=['SUUR0000SA0', 'SUUR0000SAF'],
                 apiKey = os.environ.get('BLS_API_KEY')):
    '''
    This function gets data from bls.gov using a personal api key.
    
    You need to know the series list id. You can find links to them here: https://www.bls.gov/help/hlpforma.htm
    
    Here's a description of how to deconstruct the series ID code: https://www.bls.gov/cpi/factsheets/cpi-series-ids.htm#'
    
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

#%% CPI Area Codes
def cpi_area_codes():
    '''
    You can find this information here: https://download.bls.gov/pub/time.series/cu/cu.area

    Returns
    -------
    area_code : dataframe
        Returns a dataframe of the area codes that you can use to put together a series id.
    
    Components of a series id can be found here: https://www.bls.gov/cpi/factsheets/cpi-series-ids.htm#
    
    Index Type: SU, CW, CU (we probably want SU, which is the chained CPI and is supposed to be more accurate)
    Seasonal adjustment status: U (unadjusted/not seasonally adjusted), S (seasonally adjusted)
    Periodicity: R (regular publication), S (semi-annual)
    Area code: This is what is found in this dataframe
    Item code: See a list using the cpi_item_codes function
    '''
    # Area code
    area_code = '''area_code	area_name	display_level	selectable	sort_sequence
    0000	U.S. city average	0	T	1
    0100	Northeast	0	T	5
    0110	New England	1	T	10
    0120	Middle Atlantic	1	T	11
    0200	Midwest	0	T	14
    0230	East North Central	1	T	23
    0240	West North Central	1	T	24
    0300	South	0	T	28
    0350	South Atlantic	1	T	37
    0360	East South Central	1	T	38
    0370	West South Central	1	T	39
    0400	West	0	T	43
    0480	Mountain	1	T	55
    0490	Pacific	1	T	56
    A104	Pittsburgh, PA	1	T	9
    A210	Cleveland-Akron, OH	1	T	19
    A212	Milwaukee-Racine, WI	1	T	20
    A213	Cincinnati-Hamilton, OH-KY-IN	1	T	21
    A214	Kansas City, MO-KS	1	T	22
    A311	Washington-Baltimore, DC-MD-VA-WV	1	T	36
    A421	Los Angeles-Riverside-Orange County, CA	1	T	53
    A425	Portland-Salem, OR-WA	1	T	54
    D000	Size Class D	0	T	4
    D200	Midwest - Size Class D	1	T	27
    D300	South - Size Class D	1	T	42
    N000	Size Class B/C	0	T	3
    N100	Northeast - Size Class B/C	1	T	13
    N200	Midwest - Size Class B/C	1	T	26
    N300	South - Size Class B/C	1	T	41
    N400	West - Size Class B/C	1	T	58
    S000	Size Class A	0	T	2
    S100	Northeast - Size Class A	1	T	12
    S11A	Boston-Cambridge-Newton, MA-NH	1	T	8
    S12A	New York-Newark-Jersey City, NY-NJ-PA	1	T	6
    S12B	Philadelphia-Camden-Wilmington, PA-NJ-DE-MD	1	T	7
    S200	Midwest - Size Class A	1	T	25
    S23A	Chicago-Naperville-Elgin, IL-IN-WI	1	T	15
    S23B	Detroit-Warren-Dearborn, MI	1	T	16
    S24A	Minneapolis-St.Paul-Bloomington, MN-WI	1	T	17
    S24B	St. Louis, MO-IL	1	T	18
    S300	South - Size Class A	1	T	40
    S35A	Washington-Arlington-Alexandria, DC-VA-MD-WV	1	T	34
    S35B	Miami-Fort Lauderdale-West Palm Beach, FL	1	T	32
    S35C	Atlanta-Sandy Springs-Roswell, GA	1	T	29
    S35D	Tampa-St. Petersburg-Clearwater, FL	1	T	33
    S35E	Baltimore-Columbia-Towson, MD	1	T	35
    S37A	Dallas-Fort Worth-Arlington, TX	1	T	30
    S37B	Houston-The Woodlands-Sugar Land, TX	1	T	31
    S400	West - Size Class A	1	T	57
    S48A	Phoenix-Mesa-Scottsdale, AZ	1	T	49
    S48B	Denver-Aurora-Lakewood, CO	1	T	45
    S49A	Los Angeles-Long Beach-Anaheim, CA	1	T	47
    S49B	San Francisco-Oakland-Hayward, CA	1	T	51
    S49C	Riverside-San Bernardino-Ontario, CA	1	T	48
    S49D	Seattle-Tacoma-Bellevue WA	1	T	52
    S49E	San Diego-Carlsbad, CA	1	T	50
    S49F	Urban Hawaii	1	T	46
    S49G	Urban Alaska	1	T	44
    '''
    # Convert to dataframe
    area_code = pd.read_csv(io.StringIO(area_code), sep = '\t')
    # Strip whitespace
    str_cols = ['area_code', 'area_name', 'selectable']
    area_code[str_cols] = area_code[str_cols].apply(lambda d: d.str.strip())
    
    return area_code
#%% CPI Item Codes
def cpi_item_codes():
    '''
    The list of item codes came from here: https://download.bls.gov/pub/time.series/cu/cu.item

    Returns
    -------
    item_code : dataframe
        A dataframe of item codes that you can look up to put together a series id.
        
    Components of a series id can be found here: https://www.bls.gov/cpi/factsheets/cpi-series-ids.htm#
    
    Index Type: SU, CW, CU (we probably want SU, which is the chained CPI and is supposed to be more accurate)
    Seasonal adjustment status: U (unadjusted/not seasonally adjusted), S (seasonally adjusted)
    Periodicity: R (regular publication), S (semi-annual)
    Area code: see a list using the cpi_area_codes function
    Item code: This is what is found in this dataframe
    '''
    # Item code 
    ic = '''item_code	item_name	display_level	selectable	sort_sequence
    AA0	All items - old base	0	T	2
    AA0R	Purchasing power of the consumer dollar - old base	0	T	400
    SA0	All items	0	T	1
    SA0E	Energy	1	T	375
    SA0L1	All items less food	1	T	359
    SA0L12	All items less food and shelter	1	T	362
    SA0L12E	All items less food, shelter, and energy	1	T	363
    SA0L12E4	All items less food, shelter, energy, and used cars and trucks	1	T	364
    SA0L1E	All items less food and energy	1	T	360
    SA0L2	All items less shelter	1	T	361
    SA0L5	All items less medical care	1	T	357
    SA0LE	All items less energy	1	T	358
    SA0R	Purchasing power of the consumer dollar	0	T	399
    SA311	Apparel less footwear	1	T	365
    SAA	Apparel	0	T	187
    SAA1	Men's and boys' apparel	1	T	188
    SAA2	Women's and girls' apparel	1	T	195
    SAC	Commodities	1	T	366
    SACE	Energy commodities	1	T	376
    SACL1	Commodities less food	1	T	367
    SACL11	Commodities less food and beverages	1	T	368
    SACL1E	Commodities less food and energy commodities	1	T	369
    SACL1E4	Commodities less food, energy, and used cars and trucks	1	T	370
    SAD	Durables	1	T	372
    SAE	Education and communication	0	T	311
    SAE1	Education	1	T	312
    SAE2	Communication	1	T	320
    SAE21	Information and information processing	2	T	324
    SAEC	Education and communication commodities	1	T	373
    SAES	Education and communication services	1	T	374
    SAF	Food and beverages	0	T	3
    SAF1	Food	1	T	4
    SAF11	Food at home	2	T	5
    SAF111	Cereals and bakery products	3	T	6
    SAF112	Meats, poultry, fish, and eggs	3	T	24
    SAF1121	Meats, poultry, and fish	4	T	25
    SAF11211	Meats	5	T	26
    SAF113	Fruits and vegetables	3	T	63
    SAF1131	Fresh fruits and vegetables	4	T	64
    SAF114	Nonalcoholic beverages and beverage materials	3	T	84
    SAF115	Other food at home	3	T	94
    SAF116	Alcoholic beverages	2	T	125
    SAG	Other goods and services	0	T	336
    SAG1	Personal care	1	T	340
    SAGC	Other goods	1	T	384
    SAGS	Other personal services	1	T	385
    SAH	Housing	0	T	136
    SAH1	Shelter	1	T	137
    SAH2	Fuels and utilities	1	T	145
    SAH21	Household energy	2	T	146
    SAH3	Household furnishings and operations	1	T	156
    SAH31	Household furnishings and supplies	1	T	377
    SAM	Medical care	0	T	250
    SAM1	Medical care commodities	1	T	251
    SAM2	Medical care services	1	T	256
    SAN	Nondurables	1	T	379
    SAN1D	Domestically produced farm food	1	T	371
    SANL1	Nondurables less food	1	T	380
    SANL11	Nondurables less food and beverages	1	T	382
    SANL113	Nondurables less food, beverages, and apparel	1	T	383
    SANL13	Nondurables less food and apparel	1	T	381
    SAR	Recreation	0	T	269
    SARC	Recreation commodities	1	T	387
    SARS	Recreation services	1	T	388
    SAS	Services	1	T	390
    SAS24	Utilities and public transportation	1	T	396
    SAS2RS	Rent of shelter	1	T	389
    SAS367	Other services	1	T	386
    SAS4	Transportation services	1	T	395
    SASL2RS	Services less rent of shelter	1	T	393
    SASL5	Services less medical care services	1	T	392
    SASLE	Services less energy services	1	T	391
    SAT	Transportation	0	T	210
    SAT1	Private transportation	1	T	211
    SATCLTB	Transportation commodities less motor fuel	1	T	394
    SEAA	Men's apparel	2	T	189
    SEAA01	Men's suits, sport coats, and outerwear	3	T	190
    SEAA02	Men's underwear, nightwear, swimwear and accessories	3	T	191
    SEAA03	Men's shirts and sweaters	3	T	192
    SEAA04	Men's pants and shorts	3	T	193
    SEAB	Boys' apparel	2	T	194
    SEAC	Women's apparel	2	T	196
    SEAC01	Women's outerwear	3	T	197
    SEAC02	Women's dresses	3	T	198
    SEAC03	Women's suits and separates	3	T	199
    SEAC04	Women's underwear, nightwear, swimwear and accessories	3	T	200
    SEAD	Girls' apparel	2	T	201
    SEAE	Footwear	1	T	202
    SEAE01	Men's footwear	2	T	203
    SEAE02	Boys' and girls' footwear	2	T	204
    SEAE03	Women's footwear	2	T	205
    SEAF	Infants' and toddlers' apparel	1	T	206
    SEAG	Jewelry and watches	1	T	207
    SEAG01	Watches	2	T	208
    SEAG02	Jewelry	2	T	209
    SEEA	Educational books and supplies	2	T	313
    SEEB	Tuition, other school fees, and childcare	2	T	315
    SEEB01	College tuition and fees	3	T	316
    SEEB02	Elementary and high school tuition and fees	3	T	317
    SEEB03	Day care and preschool	3	T	318
    SEEB04	Technical and business school tuition and fees	3	T	319
    SEEC	Postage and delivery services	2	T	321
    SEEC01	Postage	3	T	322
    SEEC02	Delivery services	3	T	323
    SEED	Telephone services	3	T	325
    SEED03	Wireless telephone services	4	T	326
    SEED04	Residential telephone services	4	T	327
    SEEE	Information technology, hardware and services	2	T	330
    SEEE01	Computers, peripherals, and smart home assistants	3	T	331
    SEEE02	Computer software and accessories	3	T	332
    SEEE03	Internet services and electronic information providers	3	T	333
    SEEE04	Telephone hardware, calculators, and other consumer information items	3	T	334
    SEEEC	Information technology commodities	1	T	378
    SEFA	Cereals and cereal products	4	T	7
    SEFA01	Flour and prepared flour mixes	5	T	8
    SEFA02	Breakfast cereal	5	T	9
    SEFA03	Rice, pasta, cornmeal	5	T	10
    SEFB	Bakery products	4	T	12
    SEFB01	Bread	5	T	13
    SEFB02	Fresh biscuits, rolls, muffins	5	T	16
    SEFB03	Cakes, cupcakes, and cookies	5	T	17
    SEFB04	Other bakery products	5	T	20
    SEFC	Beef and veal	6	T	27
    SEFC01	Uncooked ground beef	7	T	28
    SEFC02	Uncooked beef roasts	7	T	29
    SEFC03	Uncooked beef steaks	7	T	30
    SEFC04	Uncooked other beef and veal	7	T	31
    SEFD	Pork	6	T	32
    SEFD01	Bacon, breakfast sausage, and related products	7	T	33
    SEFD02	Ham	7	T	36
    SEFD03	Pork chops	7	T	38
    SEFD04	Other pork including roasts, steaks, and ribs	7	T	39
    SEFE	Other meats	6	T	40
    SEFF	Poultry	6	T	45
    SEFF01	Chicken	7	T	46
    SEFF02	Other uncooked poultry including turkey	6	T	49
    SEFG	Fish and seafood	5	T	50
    SEFG01	Fresh fish and seafood	6	T	51
    SEFG02	Processed fish and seafood	6	T	52
    SEFH	Eggs	4	T	55
    SEFJ	Dairy and related products	3	T	56
    SEFJ01	Milk	4	T	57
    SEFJ02	Cheese and related products	4	T	60
    SEFJ03	Ice cream and related products	4	T	61
    SEFJ04	Other dairy and related products	4	T	62
    SEFK	Fresh fruits	5	T	65
    SEFK01	Apples	6	T	66
    SEFK02	Bananas	6	T	67
    SEFK03	Citrus fruits	6	T	68
    SEFK04	Other fresh fruits	6	T	70
    SEFL	Fresh vegetables	5	T	71
    SEFL01	Potatoes	6	T	72
    SEFL02	Lettuce	6	T	73
    SEFL03	Tomatoes	6	T	74
    SEFL04	Other fresh vegetables	6	T	75
    SEFM	Processed fruits and vegetables	4	T	76
    SEFM01	Canned fruits and vegetables	5	T	77
    SEFM02	Frozen fruits and vegetables	5	T	80
    SEFM03	Other processed fruits and vegetables including dried	5	T	82
    SEFN	Juices and nonalcoholic drinks	4	T	85
    SEFN01	Carbonated drinks	5	T	86
    SEFN02	Frozen noncarbonated juices and drinks	5	T	87
    SEFN03	Nonfrozen noncarbonated juices and drinks	5	T	88
    SEFP	Beverage materials including coffee and tea	4	T	89
    SEFP01	Coffee	5	T	90
    SEFP02	Other beverage materials including tea	5	T	93
    SEFR	Sugar and sweets	4	T	95
    SEFR01	Sugar and sugar substitutes	5	T	96
    SEFR02	Candy and chewing gum	5	T	97
    SEFR03	Other sweets	5	T	98
    SEFS	Fats and oils	4	T	99
    SEFS01	Butter and margarine	5	T	100
    SEFS02	Salad dressing	5	T	103
    SEFS03	Other fats and oils including peanut butter	5	T	104
    SEFT	Other foods	4	T	106
    SEFT01	Soups	5	T	107
    SEFT02	Frozen and freeze dried prepared foods	5	T	108
    SEFT03	Snacks	5	T	109
    SEFT04	Spices, seasonings, condiments, sauces	5	T	110
    SEFT05	Baby food and formula	5	T	115
    SEFT06	Other miscellaneous foods	5	T	116
    SEFV	Food away from home	2	T	118
    SEFV01	Full service meals and snacks	3	T	119
    SEFV02	Limited service meals and snacks	3	T	120
    SEFV03	Food at employee sites and schools	3	T	121
    SEFV04	Food from vending machines and mobile vendors	3	T	123
    SEFV05	Other food away from home	3	T	124
    SEFW	Alcoholic beverages at home	3	T	126
    SEFW01	Beer, ale, and other malt beverages at home	4	T	127
    SEFW02	Distilled spirits at home	4	T	128
    SEFW03	Wine at home	4	T	131
    SEFX	Alcoholic beverages away from home	3	T	132
    SEGA	Tobacco and smoking products	1	T	337
    SEGA01	Cigarettes	2	T	338
    SEGA02	Tobacco products other than cigarettes	2	T	339
    SEGB	Personal care products	2	T	341
    SEGB01	Hair, dental, shaving, and miscellaneous personal care products	3	T	342
    SEGB02	Cosmetics, perfume, bath, nail preparations and implements	3	T	343
    SEGC	Personal care services	2	T	344
    SEGC01	Haircuts and other personal care services	3	T	345
    SEGD	Miscellaneous personal services	2	T	346
    SEGD01	Legal services	3	T	347
    SEGD02	Funeral expenses	3	T	348
    SEGD03	Laundry and dry cleaning services	3	T	349
    SEGD04	Apparel services other than laundry and dry cleaning	3	T	350
    SEGD05	Financial services	3	T	351
    SEGE	Miscellaneous personal goods	2	T	354
    SEHA	Rent of primary residence	2	T	138
    SEHB	Lodging away from home	2	T	139
    SEHB01	Housing at school, excluding board	3	T	140
    SEHB02	Other lodging away from home including hotels and motels	3	T	141
    SEHC	Owners' equivalent rent of residences	2	T	142
    SEHC01	Owners' equivalent rent of primary residence	3	T	143
    SEHD	Tenants' and household insurance	2	T	144
    SEHE	Fuel oil and other fuels	3	T	147
    SEHE01	Fuel oil	4	T	148
    SEHE02	Propane, kerosene, and firewood	4	T	149
    SEHF	Energy services	3	T	150
    SEHF01	Electricity	4	T	151
    SEHF02	Utility (piped) gas service	4	T	152
    SEHG	Water and sewer and trash collection services	2	T	153
    SEHG01	Water and sewerage maintenance	3	T	154
    SEHG02	Garbage and trash collection	3	T	155
    SEHH	Window and floor coverings and other linens	2	T	157
    SEHH01	Floor coverings	3	T	158
    SEHH02	Window coverings	3	T	159
    SEHH03	Other linens	3	T	160
    SEHJ	Furniture and bedding	2	T	161
    SEHJ01	Bedroom furniture	3	T	162
    SEHJ02	Living room, kitchen, and dining room furniture	3	T	163
    SEHJ03	Other furniture	3	T	164
    SEHK	Appliances	2	T	166
    SEHK01	Major appliances	3	T	167
    SEHK02	Other appliances	3	T	169
    SEHL	Other household equipment and furnishings	2	T	170
    SEHL01	Clocks, lamps, and decorator items	3	T	171
    SEHL02	Indoor plants and flowers	3	T	172
    SEHL03	Dishes and flatware	3	T	173
    SEHL04	Nonelectric cookware and tableware	3	T	174
    SEHM	Tools, hardware, outdoor equipment and supplies	2	T	175
    SEHM01	Tools, hardware and supplies	3	T	176
    SEHM02	Outdoor equipment and supplies	3	T	177
    SEHN	Housekeeping supplies	2	T	178
    SEHN01	Household cleaning products	3	T	179
    SEHN02	Household paper products	3	T	180
    SEHN03	Miscellaneous household products	3	T	181
    SEHP	Household operations	2	T	182
    SEHP01	Domestic services	3	T	183
    SEHP02	Gardening and lawncare services	3	T	184
    SEHP03	Moving, storage, freight expense	3	T	185
    SEHP04	Repair of household items	3	T	186
    SEMC	Professional services	2	T	257
    SEMC01	Physicians' services	3	T	258
    SEMC02	Dental services	3	T	259
    SEMC03	Eyeglasses and eye care	3	T	260
    SEMC04	Services by other medical professionals	3	T	261
    SEMD	Hospital and related services	2	T	262
    SEMD01	Hospital services	3	T	263
    SEMD02	Nursing homes and adult day services	3	T	266
    SEMD03	Care of invalids and elderly at home	3	T	267
    SEME	Health insurance	2	T	268
    SEMF	Medicinal drugs	2	T	252
    SEMF01	Prescription drugs	3	T	253
    SEMF02	Nonprescription drugs	3	T	254
    SEMG	Medical equipment and supplies	2	T	255
    SERA	Video and audio	1	T	270
    SERA01	Televisions	2	T	271
    SERA02	Cable, satellite, and live streaming television service	2	T	272
    SERA03	Other video equipment	2	T	273
    SERA04	Purchase, subscription, and rental of video	2	T	274
    SERA05	Audio equipment	2	T	277
    SERA06	Recorded music and music subscriptions	2	T	278
    SERAC	Video and audio products	1	T	397
    SERAS	Video and audio services	1	T	398
    SERB	Pets, pet products and services	1	T	279
    SERB01	Pets and pet products	2	T	280
    SERB02	Pet services including veterinary	2	T	283
    SERC	Sporting goods	1	T	286
    SERC01	Sports vehicles including bicycles	2	T	287
    SERC02	Sports equipment	2	T	288
    SERD	Photography	1	T	289
    SERD01	Photographic equipment and supplies	2	T	290
    SERD02	Photographers and photo processing	2	T	293
    SERE	Other recreational goods	1	T	296
    SERE01	Toys	2	T	297
    SERE02	Sewing machines, fabric and supplies	2	T	300
    SERE03	Music instruments and accessories	2	T	301
    SERF	Other recreation services	1	T	302
    SERF01	Club membership for shopping clubs, fraternal, or other organizations, or participant sports fees	2	T	303
    SERF02	Admissions	2	T	304
    SERF03	Fees for lessons or instructions	2	T	307
    SERG	Recreational reading materials	1	T	308
    SERG01	Newspapers and magazines	2	T	309
    SERG02	Recreational books	2	T	310
    SETA	New and used motor vehicles	2	T	212
    SETA01	New vehicles	3	T	213
    SETA02	Used cars and trucks	3	T	218
    SETA03	Leased cars and trucks	3	T	219
    SETA04	Car and truck rental	3	T	220
    SETB	Motor fuel	2	T	221
    SETB01	Gasoline (all types)	3	T	222
    SETB02	Other motor fuels	3	T	226
    SETC	Motor vehicle parts and equipment	2	T	227
    SETC01	Tires	3	T	228
    SETC02	Vehicle accessories other than tires	3	T	229
    SETD	Motor vehicle maintenance and repair	2	T	232
    SETD01	Motor vehicle body work	3	T	233
    SETD02	Motor vehicle maintenance and servicing	3	T	234
    SETD03	Motor vehicle repair	3	T	235
    SETE	Motor vehicle insurance	2	T	236
    SETF	Motor vehicle fees	2	T	237
    SETF01	State motor vehicle registration and license fees	3	T	238
    SETF03	Parking and other fees	3	T	239
    SETG	Public transportation	1	T	242
    SETG01	Airline fares	2	T	243
    SETG02	Other intercity transportation	2	T	244
    SETG03	Intracity transportation	2	T	248
    SS01031	Rice	6	T	11
    SS02011	White bread	6	T	14
    SS02021	Bread other than white	6	T	15
    SS02041	Fresh cakes and cupcakes	6	T	18
    SS02042	Cookies	6	T	19
    SS02063	Fresh sweetrolls, coffeecakes, doughnuts	6	T	21
    SS0206A	Crackers, bread, and cracker products	6	T	22
    SS0206B	Frozen and refrigerated bakery products, pies, tarts, turnovers	6	T	23
    SS04011	Bacon and related products	8	T	34
    SS04012	Breakfast sausage and related products	8	T	35
    SS04031	Ham, excluding canned	8	T	37
    SS05011	Frankfurters	7	T	41
    SS05014	Lamb and organ meats	7	T	43
    SS05015	Lamb and mutton	7	T	44
    SS0501A	Lunchmeats	7	T	42
    SS06011	Fresh whole chicken	7	T	47
    SS06021	Fresh and frozen chicken parts	7	T	48
    SS07011	Shelf stable fish and seafood	7	T	53
    SS07021	Frozen fish and seafood	7	T	54
    SS09011	Fresh whole milk	5	T	58
    SS09021	Fresh milk other than whole	5	T	59
    SS10011	Butter	6	T	101
    SS11031	Oranges, including tangerines	7	T	69
    SS13031	Canned fruits	6	T	78
    SS14011	Frozen vegetables	6	T	81
    SS14021	Canned vegetables	6	T	79
    SS14022	Dried beans, peas, and lentils	6	T	83
    SS16011	Margarine	6	T	102
    SS16014	Peanut butter	6	T	105
    SS17031	Roasted coffee	6	T	91
    SS17032	Instant coffee	6	T	92
    SS18041	Salt and other seasonings and spices	6	T	111
    SS18042	Olives, pickles, relishes	6	T	112
    SS18043	Sauces and gravies	6	T	113
    SS1804B	Other condiments	6	T	114
    SS18064	Prepared salads	6	T	117
    SS20021	Whiskey at home	5	T	129
    SS20022	Distilled spirits, excluding whiskey, at home	5	T	130
    SS20051	Beer, ale, and other malt beverages away from home	4	T	133
    SS20052	Wine away from home	4	T	134
    SS20053	Distilled spirits away from home	4	T	135
    SS27051	Land-line interstate toll calls	5	T	328
    SS27061	Land-line intrastate toll calls	5	T	329
    SS30021	Laundry equipment	4	T	168
    SS31022	Video discs and other media	3	T	275
    SS31023	Video game hardware, software and accessories	3	T	299
    SS33032	Stationery, stationery supplies, gift wrap	3	T	355
    SS45011	New cars	4	T	215
    SS4501A	New cars and trucks	4	T	214
    SS45021	New trucks	4	T	216
    SS45031	New motorcycles	4	T	217
    SS47014	Gasoline, unleaded regular	4	T	223
    SS47015	Gasoline, unleaded midgrade	4	T	224
    SS47016	Gasoline, unleaded premium	4	T	225
    SS47021	Motor oil, coolant, and fluids	4	T	231
    SS48021	Vehicle parts and equipment other than tires	4	T	230
    SS52051	Parking fees and tolls	4	T	240
    SS53021	Intercity bus fare	3	T	245
    SS53022	Intercity train fare	3	T	246
    SS53023	Ship fare	3	T	247
    SS53031	Intracity mass transit	3	T	249
    SS5702	Inpatient hospital services	4	T	264
    SS5703	Outpatient hospital services	4	T	265
    SS61011	Toys, games, hobbies and playground equipment	3	T	298
    SS61021	Film and photographic supplies	3	T	291
    SS61023	Photographic equipment	3	T	292
    SS61031	Pet food	3	T	281
    SS61032	Purchase of pets, pet supplies, accessories	3	T	282
    SS62011	Automobile service clubs	4	T	241
    SS62031	Admission to movies, theaters, and concerts	3	T	305
    SS62032	Admission to sporting events	3	T	306
    SS62051	Photographer fees	3	T	294
    SS62052	Photo Processing	3	T	295
    SS62053	Pet services	3	T	284
    SS62054	Veterinarian services	3	T	285
    SS62055	Subscription and rental of video and video games	3	T	276
    SS68021	Checking account and other bank services	4	T	352
    SS68023	Tax return preparation and other accounting fees	4	T	353
    SSEA011	College textbooks	3	T	314
    SSEE041	Smartphones	4	T	335
    SSFV031A	Food at elementary and secondary schools	3	T	122
    SSGE013	Infants' equipment	3	T	356
    SSHJ031	Infants' furniture	3	T	165
    '''
    # Convert to dataframe
    item_code = pd.read_csv(io.StringIO(ic), sep = '\t')
    
    # Remove whitespace
    str_cols = ['item_code', 'item_name', 'selectable']
    item_code[str_cols] = item_code[str_cols].apply(lambda d: d.str.strip())
    
    return item_code
